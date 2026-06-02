from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import List
import models, schemas, database, auth
from repositories.visit_repository import VisitRepository
from repositories.inquiry_repository import InquiryRepository
from repositories.property_repository import PropertyRepository
from utils.security import encrypt_telegram_id, decrypt_telegram_id

router = APIRouter(
    tags=["Visits & Scheduling"]
)

@router.post("/visits/book", response_model=schemas.VisitResponse)
def book_visit(
    payload: schemas.VisitCreate,
    db: Session = Depends(database.get_db)
):
    """Called by n8n after a Google Calendar event is successfully created."""
    # Convert to UTC to match original behavior
    visit_date_utc = payload.visit_date.astimezone(timezone.utc)
    
    # Restrict bookings to weekdays (Monday-Friday) only
    tunis_tz = ZoneInfo("Africa/Tunis")
    visit_tunis = visit_date_utc.replace(tzinfo=timezone.utc).astimezone(tunis_tz)
    if visit_tunis.weekday() in (5, 6):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Visits cannot be booked on Saturdays or Sundays."
        )
    
    # Dynamically resolve client identity if telegram_chat_id is linked to a registered web user
    client_id = None
    encrypted_chat_id = None
    if payload.client_telegram_id:
        encrypted_chat_id = encrypt_telegram_id(payload.client_telegram_id)
        user = db.query(models.User).filter(models.User.telegram_chat_id == encrypted_chat_id).first()
        if user:
            client_id = user.id
            
    new_visit = models.Visit(
        property_id=payload.property_id,
        client_id=client_id,
        agent_id=payload.agent_id,
        visit_date=visit_date_utc,
        telegram_chat_id=encrypted_chat_id,
        status="scheduled",
        reminder_sent=False
    )
    return VisitRepository.save(db, new_visit)

@router.put("/visits/update",response_model=schemas.VisitResponse)
def update_visit(
    payload:schemas.VisitUpdateDB,
    db:Session=Depends(database.get_db)
):
    """ resheduel a visit """
    original_date_utc=payload.original_visit_date.astimezone(timezone.utc)
    new_date_utc=payload.new_visit_date.astimezone(timezone.utc)
    
    # Restrict updates/rescheduling to weekdays (Monday-Friday) only
    tunis_tz = ZoneInfo("Africa/Tunis")
    new_date_tunis = new_date_utc.replace(tzinfo=timezone.utc).astimezone(tunis_tz)
    if new_date_tunis.weekday() in (5, 6):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Visits cannot be rescheduled to Saturdays or Sundays."
        )
        
    encrypted_chat_id = encrypt_telegram_id(payload.client_telegram_id)
    visit=VisitRepository.find_scheduled_visit(
        db=db,
        telegram_chat_id=encrypted_chat_id,
        property_id=payload.property_id,
        visit_date=original_date_utc,
    )
    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="no visit found",
        )
    visit.visit_date=new_date_utc
    visit.status="scheduled"
    visit.reminder_sent=False
    VisitRepository.commit(db)
    db.refresh(visit)
    return visit

@router.post("/visits/cancel")
def cancel_visit(
    payload:schemas.VisitCancelDB,
    db:Session=Depends(database.get_db)
):
    """
    cancel a visit
    """
    visit_date_utc = payload.visit_date.astimezone(timezone.utc) 
    # retrieve it from the database 
    encrypted_chat_id = encrypt_telegram_id(payload.client_telegram_id)
    # retrieve it from the database 
    visit = VisitRepository.find_scheduled_visit(
        db=db,
        telegram_chat_id=encrypted_chat_id, 
        property_id=payload.property_id,
        visit_date=visit_date_utc 
    )
    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="no visit found" 
        )
        
    visit.status = "cancelled"
    VisitRepository.commit(db)
    return {
        "status": "success", 
        "message": "Visit marked as cancelled successfully"
    }
    




    
@router.get("/visits/agent-availability")
def check_agent_availability(
    agent_id: int,
    requested_date: str,
    db: Session = Depends(database.get_db)
):
    """
    Checks if a sub-agent is available at a requested date/time based on their scheduled visits in the DB.
    Returns whether they are available, and a list of 5 upcoming available time slots (in Tunis time, UTC+1).
    """
    # 1. Parse requested date/time
    tunis_tz = ZoneInfo("Africa/Tunis")
    try:
        parsed_date = datetime.fromisoformat(requested_date.replace("Z", "+00:00"))
    except ValueError:
        try:
            # Fallback to date only: assume 06:00 local Tunis time
            parsed_date = datetime.strptime(requested_date, "%Y-%m-%d")
            parsed_date = parsed_date.replace(hour=6, minute=0, second=0, tzinfo=tunis_tz)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD or ISO 8601 format.")
            
    # 2. Standardize parsed_date to naive UTC
    if parsed_date.tzinfo is not None:
        parsed_date_utc = parsed_date.astimezone(timezone.utc).replace(tzinfo=None)
    else:
        # If naive, treat it as Africa/Tunis local time, then convert to UTC
        parsed_date_tz = parsed_date.replace(tzinfo=tunis_tz)
        parsed_date_utc = parsed_date_tz.astimezone(timezone.utc).replace(tzinfo=None)
        
    # 3. Ensure the start date is not in the past relative to UTC 'now'
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    if parsed_date_utc < now_utc:
        parsed_date_utc = now_utc
        
    # 4. Fetch all scheduled visits for this agent
    visits = db.query(models.Visit).filter(
        models.Visit.agent_id == agent_id,
        models.Visit.status == "scheduled"
    ).all()
    
    # 5. Check if the specific requested slot is available
    is_available = True
    requested_tunis = parsed_date_utc.replace(tzinfo=timezone.utc).astimezone(tunis_tz)
    
    # Working hours constraint: 06:00 to 23:00 Tunis time (starts must be between 06:00 and 22:00 inclusive)
    # Also restrict availability to weekdays (Monday-Friday) only
    if not (6 <= requested_tunis.hour <= 22) or requested_tunis.weekday() in (5, 6):
        is_available = False
    else:
        for visit in visits:
            diff = abs((parsed_date_utc - visit.visit_date).total_seconds())
            if diff < 3600:
                is_available = False
                break
            
    # 6. Find 5 available slots starting from parsed_date_utc
    available_slots = []
    current_time_utc = parsed_date_utc
    # Round to clean hour if minutes/seconds/microseconds exist
    if current_time_utc.minute > 0 or current_time_utc.second > 0 or current_time_utc.microsecond > 0:
        current_time_utc = current_time_utc.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        
    checked_slots = 0
    # Search up to 1 week (168 hours) to prevent infinite loops
    while len(available_slots) < 5 and checked_slots < 168:
        # Convert slot time in UTC to Tunis time (Africa/Tunis)
        tunis_time = current_time_utc.replace(tzinfo=timezone.utc).astimezone(tunis_tz)
        hour = tunis_time.hour
        
        # Candidate slot must be within working hours and NOT on Saturday (5) or Sunday (6)
        if 6 <= hour <= 22 and tunis_time.weekday() not in (5, 6):
            conflict = False
            for visit in visits:
                diff = abs((current_time_utc - visit.visit_date).total_seconds())
                if diff < 3600:
                    conflict = True
                    break
            if not conflict:
                available_slots.append(tunis_time.isoformat(timespec='seconds'))
                
        current_time_utc += timedelta(hours=1)
        checked_slots += 1
        
    return {
        "agent_id": agent_id,
        "is_available": is_available,
        "available_slots": available_slots
    }


@router.get("/visits/upcoming", response_model=List[schemas.VisitDetailResponse])
def get_upcoming_visits(
    db: Session = Depends(database.get_db)
):
    """Returns visits scheduled within a short window for testing."""
    now = datetime.now(timezone.utc).replace(tzinfo=None) # naive for compare
    
    # Old logic (40-50 min window):
    # window_start = now + timedelta(minutes=40)
    # window_end = now + timedelta(minutes=50)
    
    # Testing logic: wider window (e.g., 24 hours) for easier testing
    window_start = now - timedelta(minutes=10)  # include slightly past visits to avoid race conditions
    window_end = now + timedelta(hours=24)
    
    return VisitRepository.get_upcoming(db, window_start, window_end)

@router.put("/visits/{visit_id}/reminder-sent")
def mark_reminder_sent(
    visit_id: int,
    db: Session = Depends(database.get_db)
):
    """Marks a visit as notified."""
    visit = VisitRepository.get_by_id(db, visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    visit.reminder_sent = True
    VisitRepository.commit(db)
    return {"message": "Reminder marked as sent"}

@router.get("/agent/inquiries")
def get_agent_inquiries(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """
    Returns pending transaction requests for approval.
    """
    sub_agent_ids = None
    owner_id = None
    agent_id = None

    if current_user.role == "admin":
        pass # All
    elif current_user.role == "head_agent":
        owner_id = current_user.id
        sub_agent_ids = [u.id for u in db.query(models.User.id).filter(models.User.manager_id == current_user.id).all()]
    else:
        agent_id = current_user.id

    requests = InquiryRepository.get_pending_detailed(db, agent_id=agent_id, sub_agent_ids=sub_agent_ids, owner_id=owner_id)

    result = []
    for r in requests:
        prop = r.property
        agent = r.agent
        client = r.client
        
        # Build descriptive message
        msg = f"Agent {agent.full_name if agent else 'System'} requested approval for a {r.type.lower()}."
        if r.type == "Rent" and r.rent_start_date and r.rent_end_date:
            msg += f" Dates: {r.rent_start_date.strftime('%Y-%m-%d')} to {r.rent_end_date.strftime('%Y-%m-%d')}."
        
        result.append({
            "id": r.id,
            "name": client.full_name if client else "New Client",
            "email": client.email if client else "",
            "phone": client.phone_number if client else "",
            "subject": f"{r.type} Request: {prop.title if prop else 'Property'}",
            "message": msg,
            "status": r.status, # Use actual request status
            "property_id": r.property_id,
            "agent_id": r.agent_id,
            "client_id": r.client_id,
            "price": float(r.price) if r.price else 0,
            "request_type": r.type.upper()
        })
    
    return result

from utils.reporting import finalize_transaction

@router.put("/agent/inquiries/{inquiry_id}/status")
def update_inquiry_status(
    inquiry_id: int,
    status: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Handles Approval/Rejection of a TransactionRequest."""
    req = InquiryRepository.get_by_id(db, inquiry_id)
    if not req:
        raise HTTPException(status_code=404, detail="Transaction request not found")
    
    # Check if user is authorized to approve/reject
    prop = PropertyRepository.get_by_id(db, req.property_id)
    requester = db.query(models.User).filter(models.User.id == req.agent_id).first()
    
    is_admin = current_user.role == "admin"
    is_owner = prop.owner_id == current_user.id
    is_manager = current_user.role == "head_agent" and requester and requester.manager_id == current_user.id
    
    if not (is_admin or is_owner or is_manager):
        raise HTTPException(status_code=403, detail="Not authorized to approve this request")

    if status == "replied": # APPROVE
        req.status = "approved"
        prop.status = "approved_sold" if req.type == "Sale" else "approved_rent"
        InquiryRepository.commit(db)
        return {"message": "Request approved. Sub-agent can now finalize the transaction."}
    
    elif status == "closed": # REJECT
        req.status = "rejected"
        prop.status = "available"
        InquiryRepository.commit(db)
        return {"message": "Request rejected and property marked available again."}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid status action")

@router.get("/agent/visits", response_model=List[schemas.VisitDetailResponse])
def get_agent_visits_list(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """Simple list of visits for the current agent."""
    if current_user.role == "admin":
        return VisitRepository.get_all_detailed(db)
    elif current_user.role == "head_agent":
        managed_user_ids_query = db.query(models.User.id).filter(models.User.manager_id == current_user.id).all()
        allowed_agent_ids = [current_user.id] + [uid[0] for uid in managed_user_ids_query]
        return VisitRepository.get_all_detailed(db, agent_ids=allowed_agent_ids)
    
    return VisitRepository.get_all_detailed(db, agent_ids=[current_user.id])

@router.put("/agent/visits/{visit_id}/status")
def update_visit_status(
    visit_id: int,
    status: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """Updates a visit status."""
    vis = VisitRepository.get_with_property_and_owner(db, visit_id)
    if not vis:
        raise HTTPException(status_code=404, detail="Visit not found")
        
    # Authorization: Admin, Assigned Agent, Property Owner, or Owner's Manager
    is_admin = current_user.role == "admin"
    is_assigned = vis.agent_id == current_user.id
    is_owner = vis.property and vis.property.owner_id == current_user.id
    is_manager = current_user.role == "head_agent" and vis.property and vis.property.owner and vis.property.owner.manager_id == current_user.id
    
    if not (is_admin or is_assigned or is_owner or is_manager):
        raise HTTPException(status_code=403, detail="Not authorized to update this visit")

    vis.status = status
    VisitRepository.commit(db)
    return {"message": "Visit status updated"}

@router.get("/agency/clients", response_model=List[schemas.User])
def get_clients_list(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """Returns all registered clients."""
    return VisitRepository.list_clients(db)

@router.post("/visits/send-reminder-email")
def send_visit_reminder_email(
    payload: schemas.EmailSendRequest,
    background_tasks: BackgroundTasks
):
    """Sends a visit reminder HTML email to the specified agent."""
    from services import email
    background_tasks.add_task(
        email.send_html_email,
        to_email=payload.to_email,
        subject=payload.subject,
        html_content=payload.html_content
    )
    return {"status": "success", "message": "Email queued for delivery"}

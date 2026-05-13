from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta, timezone
from typing import List
import models, schemas, database, auth

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
    
    new_visit = models.Visit(
        property_id=payload.property_id,
        client_id=None,
        agent_id=payload.agent_id,
        visit_date=visit_date_utc,
        telegram_chat_id=payload.client_telegram_id,
        status="scheduled",
        reminder_sent=False
    )
    db.add(new_visit)
    db.commit()
    db.refresh(new_visit)
    return new_visit

@router.get("/visits/upcoming", response_model=List[schemas.VisitResponse])
def get_upcoming_visits(
    db: Session = Depends(database.get_db)
):
    """Returns visits scheduled within the next window (40-50 min) as per original logic."""
    now = datetime.now(timezone.utc).replace(tzinfo=None) # naive for compare
    window_start = now
    window_end = now + timedelta(minutes=60)
    
    return db.query(models.Visit).filter(
        models.Visit.status == 'scheduled',
        models.Visit.reminder_sent == False,
        models.Visit.visit_date >= window_start,
        models.Visit.visit_date <= window_end
    ).all()

@router.put("/visits/{visit_id}/reminder-sent")
def mark_reminder_sent(
    visit_id: int,
    db: Session = Depends(database.get_db)
):
    """Marks a visit as notified."""
    visit = db.query(models.Visit).filter(models.Visit.id == visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    visit.reminder_sent = True
    db.commit()
    return {"message": "Reminder marked as sent"}

@router.get("/agent/inquiries")
def get_agent_inquiries(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """
    Returns pending transaction requests for approval.
    - Admins: See all pending requests.
    - Head Agents: See requests for their properties OR from their team.
    - Agents: See only their own submitted requests.
    """
    query = db.query(models.TransactionRequest).options(
        joinedload(models.TransactionRequest.property),
        joinedload(models.TransactionRequest.agent),
        joinedload(models.TransactionRequest.client)
    ).filter(models.TransactionRequest.status == "pending")

    if current_user.role == "head_agent":
        # Get IDs of sub-agents managed by this head agent
        sub_agent_ids = [u.id for u in db.query(models.User.id).filter(models.User.manager_id == current_user.id).all()]
        
        # Explicitly join on the relationship to avoid any ambiguity
        query = query.join(models.TransactionRequest.property).filter(
            (models.Property.owner_id == current_user.id) | 
            (models.TransactionRequest.agent_id.in_(sub_agent_ids))
        )
    elif current_user.role == "agent":
        query = query.filter(models.TransactionRequest.agent_id == current_user.id)
    
    requests = query.order_by(models.TransactionRequest.created_at.desc()).all()

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
            "status": "new", # Compatibility field for UI
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
    """
    Handles Approval/Rejection of a TransactionRequest.
    - status 'replied' -> Approved
    - status 'closed' -> Rejected
    """
    req = db.query(models.TransactionRequest).filter(models.TransactionRequest.id == inquiry_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Transaction request not found")
    
    # Check if user is authorized to approve/reject
    prop = db.query(models.Property).filter(models.Property.id == req.property_id).first()
    requester = db.query(models.User).filter(models.User.id == req.agent_id).first()
    
    is_admin = current_user.role == "admin"
    is_owner = prop.owner_id == current_user.id
    is_manager = current_user.role == "head_agent" and requester and requester.manager_id == current_user.id
    
    if not (is_admin or is_owner or is_manager):
        raise HTTPException(status_code=403, detail="Not authorized to approve this request")

    if status == "replied": # APPROVE
        req.status = "approved"
        
        # Finalize Property
        prop.status = "sold" if req.type == "Sale" else "rented"
        prop.buyer_id = req.client_id
        if req.type == "Rent":
            prop.rent_start_date = req.rent_start_date
            prop.rent_end_date = req.rent_end_date
        
        # Generate Report
        finalize_transaction(db, prop, req.type, background_tasks)
        db.commit()
        return {"message": "Request approved and transaction finalized."}
    
    elif status == "closed": # REJECT
        req.status = "rejected"
        # Revert property status back to available
        prop.status = "available"
        db.commit()
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
        return db.query(models.Visit).options(
            joinedload(models.Visit.property),
            joinedload(models.Visit.client),
            joinedload(models.Visit.agent)
        ).all()
    elif current_user.role == "head_agent":
        managed_user_ids_query = db.query(models.User.id).filter(models.User.manager_id == current_user.id).all()
        allowed_agent_ids = [current_user.id] + [uid[0] for uid in managed_user_ids_query]
        return db.query(models.Visit).options(
            joinedload(models.Visit.property),
            joinedload(models.Visit.client),
            joinedload(models.Visit.agent)
        ).filter(models.Visit.agent_id.in_(allowed_agent_ids)).order_by(models.Visit.visit_date.asc()).all()
    
    return db.query(models.Visit).options(
        joinedload(models.Visit.property),
        joinedload(models.Visit.client),
        joinedload(models.Visit.agent)
    ).filter(models.Visit.agent_id == current_user.id).order_by(models.Visit.visit_date.asc()).all()

@router.put("/agent/visits/{visit_id}/status")
def update_visit_status(
    visit_id: int,
    status: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """Updates a visit status."""
    vis = db.query(models.Visit).options(joinedload(models.Visit.property).joinedload(models.Property.owner)).filter(models.Visit.id == visit_id).first()
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
    db.commit()
    return {"message": "Visit status updated"}

@router.get("/agency/clients", response_model=List[schemas.User])
def get_clients_list(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """Returns all registered clients."""
    return db.query(models.User).filter(models.User.role == "client").all()

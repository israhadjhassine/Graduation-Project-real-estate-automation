from fastapi import APIRouter, Depends, HTTPException, status
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
    """Returns visits/inquiries for agents, formatted exactly as original main.py."""
    if current_user.role == "admin":
        visits = db.query(models.Visit).order_by(models.Visit.created_at.desc()).all()
    elif current_user.role == "head_agent":
        # Properties owned by the head agent OR properties owned by users managed by the head agent
        managed_user_ids_query = db.query(models.User.id).filter(models.User.manager_id == current_user.id).all()
        allowed_owner_ids = [current_user.id] + [uid[0] for uid in managed_user_ids_query]
        
        visits = db.query(models.Visit).join(
            models.Property, models.Visit.property_id == models.Property.id
        ).filter(
            models.Property.owner_id.in_(allowed_owner_ids)
        ).order_by(models.Visit.created_at.desc()).all()
    else:
        visits = db.query(models.Visit).filter(
            models.Visit.agent_id == current_user.id
        ).order_by(models.Visit.created_at.desc()).all()

    result = []
    for v in visits:
        prop = db.query(models.Property).filter(models.Property.id == v.property_id).first()
        result.append({
            "id": v.id,
            "name": f"Client #{v.telegram_chat_id or v.client_id or 'Unknown'}",
            "email": "",
            "phone": v.telegram_chat_id or "",
            "subject": f"Visit request: {prop.title if prop else 'Property'}",
            "message": f"Scheduled for {v.visit_date.strftime('%Y-%m-%d %H:%M') if v.visit_date else 'TBD'}",
            "status": "new" if v.status == "scheduled" else "replied" if v.status == "finished" else "closed",
            "source": "telegram" if v.telegram_chat_id else "web",
            "property_id": v.property_id,
            "property_status": prop.status if prop else None,
            "visit_id": v.id,
            "visit_status": v.status
        })
    
    if current_user.role in ["head_agent", "admin"]:
        managed_user_ids_query = db.query(models.User.id).filter(models.User.manager_id == current_user.id).all()
        allowed_owner_ids = [current_user.id] + [uid[0] for uid in managed_user_ids_query]

        pending_props = db.query(models.Property).filter(
            models.Property.status.in_(["pending_sold", "pending_rent"]),
            models.Property.owner_id.in_(allowed_owner_ids) if current_user.role == "head_agent" else True
        ).all()
        for p in pending_props:
            agent = db.query(models.User).filter(models.User.id == p.agent_id).first() if p.agent_id else None
            buyer = db.query(models.User).filter(models.User.id == p.buyer_id).first() if p.buyer_id else None
            if not any(r["property_id"] == p.id for r in result):
                req_type = "Sale" if p.status == "pending_sold" else "Rent"
                status_display = "sold" if p.status == "pending_sold" else "rented"
                msg = f"Sub-Agent {agent.full_name if agent else 'unknown'} is requesting approval to mark this property as {status_display}."
                if buyer: msg += f" Client Email: {buyer.email}."
                if p.status == "pending_rent" and p.rent_start_date and p.rent_end_date:
                    msg += f" Duration: {p.rent_start_date.strftime('%b %d, %Y')} to {p.rent_end_date.strftime('%b %d, %Y')}."
                
                result.insert(0, {
                    "id": -p.id,
                    "name": agent.full_name if agent else "Sub-Agent",
                    "email": agent.email if agent else "",
                    "phone": "",
                    "subject": f"{req_type} Request: {p.title}",
                    "message": msg,
                    "status": "new",
                    "source": "system",
                    "property_id": p.id,
                    "property_status": p.status,
                    "visit_id": None,
                    "visit_status": None
                })
    return result

@router.put("/agent/inquiries/{inquiry_id}/status")
def update_inquiry_status(
    inquiry_id: int,
    status: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """Maps inquiry status back to visit status."""
    vis = db.query(models.Visit).filter(models.Visit.id == inquiry_id).first()
    if not vis:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    status_map = {"new": "scheduled", "replied": "finished", "closed": "cancelled"}
    vis.status = status_map.get(status, status)
    db.commit()
    return {"message": "Status updated"}

@router.get("/agent/visits", response_model=List[schemas.VisitResponse])
def get_agent_visits_list(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """Simple list of visits for the current agent."""
    if current_user.role == "admin":
        return db.query(models.Visit).all()
    elif current_user.role == "head_agent":
        managed_user_ids_query = db.query(models.User.id).filter(models.User.manager_id == current_user.id).all()
        allowed_agent_ids = [current_user.id] + [uid[0] for uid in managed_user_ids_query]
        return db.query(models.Visit).filter(models.Visit.agent_id.in_(allowed_agent_ids)).order_by(models.Visit.visit_date.asc()).all()
    
    return db.query(models.Visit).filter(models.Visit.agent_id == current_user.id).order_by(models.Visit.visit_date.asc()).all()

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

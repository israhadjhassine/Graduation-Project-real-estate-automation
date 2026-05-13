from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
import os, models, auth, database, tempfile, io
from services import email
from utils.reporting import generate_transaction_report, finalize_transaction

router = APIRouter(
    tags=["Reports & Approvals"]
)

@router.post("/agency/properties/{property_id}/approve-sale")
def approve_property_sale(
    property_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Head Agent approves sale and marks as sold."""
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if current_user.role == "head_agent" and prop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # We allow approval if it's pending_sold, but with the new workflow it might go straight to sold.
    # However, for backward compatibility or direct manual approval:
    if prop.status != "pending_sold":
        raise HTTPException(status_code=400, detail="Property is not pending a sale approval")
    
    finalize_transaction(db, prop, "Sale", background_tasks)
    return {"message": "Sale approved. Report record created and notifications sent."}

@router.post("/agency/properties/{property_id}/reject-sale")
def reject_property_sale(
    property_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Reverts property to available."""
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if current_user.role == "head_agent" and prop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    prop.status = "available"
    # Capture agent details before clearing
    agent = db.query(models.User).filter(models.User.id == prop.agent_id).first() if prop.agent_id else None
    db.commit()

    # Notify Sub-Agent of Rejection
    if agent and agent.email:
        background_tasks.add_task(
            email.send_transaction_rejection_email,
            sub_agent_email=agent.email,
            sub_agent_name=agent.full_name,
            property_title=prop.title,
            tx_type="Sale",
            manager_name=current_user.full_name
        )

    return {"message": "Sale rejected. Property reverted to available."}

@router.post("/agency/properties/{property_id}/approve-rent")
def approve_property_rent(
    property_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Approves rent and marks as rented."""
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if current_user.role == "head_agent" and prop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if prop.status != "pending_rent":
        raise HTTPException(status_code=400, detail="Property is not pending a rent approval")
    
    finalize_transaction(db, prop, "Rent", background_tasks)
    return {"message": "Rent approved. Property is now marked as rented and report generated."}

@router.post("/agency/properties/{property_id}/reject-rent")
def reject_property_rent(
    property_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Reverts property to available."""
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if current_user.role == "head_agent" and prop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    prop.status = "available"
    prop.rent_start_date = None
    prop.rent_end_date = None

    # Capture agent details
    agent = db.query(models.User).filter(models.User.id == prop.agent_id).first() if prop.agent_id else None
    db.commit()

    # Notify Sub-Agent of Rejection
    if agent and agent.email:
        background_tasks.add_task(
            email.send_transaction_rejection_email,
            sub_agent_email=agent.email,
            sub_agent_name=agent.full_name,
            property_title=prop.title,
            tx_type="Rent",
            manager_name=current_user.full_name
        )

    return {"message": "Rent rejected. Property reverted to available."}

@router.get("/admin/reports")
def list_reports(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["admin", "head_agent"]))
):
    """Returns a list of available transaction reports from database."""
    reports = db.query(models.Report).order_by(models.Report.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "property_title": r.property.title if r.property else "Unknown",
            "type": r.transaction_type,
            "date": r.created_at.strftime("%Y-%m-%d %H:%M"),
            "price": f"{r.price_at_time:,}" if r.price_at_time else "N/A"
        } for r in reports
    ]

@router.get("/admin/reports/{report_id}/download")
def download_report(
    report_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["admin", "head_agent"]))
):
    """Generates and downloads a specific transaction report on-the-fly."""
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report record not found")
    
    prop = report.property
    if not prop:
        raise HTTPException(status_code=404, detail="Associated property not found")
        
    # Generate to a temporary file
    pdf_path = generate_transaction_report(db, prop, report.transaction_type)
    
    return FileResponse(
        pdf_path, 
        filename=f"Report_{report.transaction_type}_{prop.id}.pdf",
        media_type="application/pdf"
    )

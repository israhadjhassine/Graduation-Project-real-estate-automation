from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
import os, models, auth, database
from services import email

router = APIRouter(
    tags=["Reports & Approvals"]
)

def generate_transaction_report_txt(db, prop, tx_type):
    """Restored original .txt report generation logic."""
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/Transaction_Prop{prop.id}_{tx_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
    agent = db.query(models.User).get(prop.agent_id) if prop.agent_id else None
    owner = db.query(models.User).get(prop.owner_id) if prop.owner_id else None
    buyer = db.query(models.User).get(prop.buyer_id) if prop.buyer_id else None
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"=== {tx_type.upper()} TRANSACTION REPORT ===\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("[PROPERTY DETAILS]\n")
        f.write(f"ID: {prop.id}\n")
        f.write(f"Title: {prop.title}\n")
        f.write(f"Location: {prop.city}, {prop.country}\n")
        f.write(f"Price: {prop.price} {prop.currency}\n")
        if tx_type == "Rent" and prop.rent_start_date:
            f.write(f"Rent Duration: {prop.rent_start_date.strftime('%Y-%m-%d')} to {prop.rent_end_date.strftime('%Y-%m-%d')}\n")
        f.write("\n")
        f.write("[STAFF DETAILS]\n")
        f.write(f"Head Agent: {owner.full_name if owner else 'None'} ({owner.email if owner else 'N/A'})\n")
        f.write(f"Sub Agent: {agent.full_name if agent else 'None'} ({agent.email if agent else 'N/A'})\n\n")
        f.write("[CLIENT/BUYER DETAILS]\n")
        if buyer:
            f.write(f"Name: {buyer.full_name}\n")
            f.write(f"Email: {buyer.email}\n")
            f.write(f"Phone: {buyer.phone_number or 'N/A'}\n")
        else:
            f.write("No client specified in this transaction.\n")
    return filename

@router.post("/agency/properties/{property_id}/approve-sale")
def approve_property_sale(
    property_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Head Agent approves sale and marks as sold."""
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if current_user.role == "head_agent" and prop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    if prop.status != "pending_sold":
        raise HTTPException(status_code=400, detail="Property is not pending a sale approval")
    
    prop.status = "sold"
    generate_transaction_report_txt(db, prop, "Sale")
    db.commit()
    return {"message": "Sale approved. Property is now marked as sold."}

@router.post("/agency/properties/{property_id}/reject-sale")
def reject_property_sale(
    property_id: int,
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
    db.commit()
    return {"message": "Sale rejected. Property reverted to available."}

@router.post("/agency/properties/{property_id}/approve-rent")
def approve_property_rent(
    property_id: int,
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
    
    prop.status = "rented"
    generate_transaction_report_txt(db, prop, "Rent")
    db.commit()
    return {"message": "Rent approved. Property is now marked as rented."}

@router.post("/agency/properties/{property_id}/reject-rent")
def reject_property_rent(
    property_id: int,
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
    db.commit()
    return {"message": "Rent rejected. Property reverted to available."}

@router.get("/admin/reports")
def list_reports(current_user: models.User = Depends(auth.RoleChecker(["admin"]))):
    """Returns a list of available transaction reports."""
    if not os.path.exists("reports"):
        return []
    return [{"name": f} for f in os.listdir("reports") if f.endswith(".txt")]

@router.get("/admin/reports/{filename}")
def download_report(filename: str, current_user: models.User = Depends(auth.RoleChecker(["admin"]))):
    """Downloads a specific transaction report."""
    file_path = os.path.join("reports", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(file_path, filename=filename)

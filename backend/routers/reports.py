from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime
import os, models, auth, database
from services import email

router = APIRouter(
    tags=["Reports & Approvals"]
)

from fpdf import FPDF

def generate_transaction_report(db, prop, tx_type):
    """Restored professional PDF report generation logic."""
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/Transaction_Prop{prop.id}_{tx_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    agent = db.query(models.User).filter(models.User.id == prop.agent_id).first() if prop.agent_id else None
    owner = db.query(models.User).filter(models.User.id == prop.owner_id).first() if prop.owner_id else None
    buyer = db.query(models.User).filter(models.User.id == prop.buyer_id).first() if prop.buyer_id else None
    
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("helvetica", "B", 20)
    pdf.set_text_color(30, 41, 59) # Slate 800
    pdf.cell(0, 20, f"{tx_type.upper()} TRANSACTION REPORT", ln=True, align="C")
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(100, 116, 139) # Slate 500
    pdf.cell(0, 5, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
    pdf.ln(10)
    
    # Property Section
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 10, "PROPERTY DETAILS", ln=True)
    pdf.set_draw_color(226, 232, 240)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
    pdf.ln(2)
    
    pdf.set_font("helvetica", "", 12)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(50, 8, txt="Property ID:", border=0)
    pdf.cell(0, 8, txt=str(prop.id), border=0, ln=1)
    
    pdf.cell(50, 8, txt="Title:", border=0)
    pdf.multi_cell(0, 8, txt=prop.title, border=0, align="L")
    
    pdf.cell(50, 8, txt="Location:", border=0)
    pdf.cell(0, 8, txt=f"{prop.city}, {prop.country}", border=0, ln=1)
    
    pdf.cell(50, 8, txt="Price:", border=0)
    pdf.cell(0, 8, txt=f"{prop.price:,} {prop.currency}", border=0, ln=1)
    
    if tx_type == "Rent" and prop.rent_start_date:
        pdf.cell(50, 8, txt="Rent Duration:", border=0)
        pdf.cell(0, 8, txt=f"{prop.rent_start_date.strftime('%Y-%m-%d')} to {prop.rent_end_date.strftime('%Y-%m-%d')}", border=0, ln=1)
    pdf.ln(10)
    
    # Staff Section
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 10, txt="STAFF DETAILS", ln=True)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
    pdf.ln(2)
    
    pdf.set_font("helvetica", "", 12)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(50, 8, txt="Head Agent:", border=0)
    pdf.cell(0, 8, txt=f"{owner.full_name if owner else 'None'} ({owner.email if owner else 'N/A'})", border=0, ln=1)
    
    pdf.cell(50, 8, txt="Sub Agent:", border=0)
    pdf.cell(0, 8, txt=f"{agent.full_name if agent else 'None'} ({agent.email if agent else 'N/A'})", border=0, ln=1)
    pdf.ln(10)
    
    # Client Section
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 10, txt="CLIENT / BUYER DETAILS", ln=True)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
    pdf.ln(2)
    
    pdf.set_font("helvetica", "", 12)
    pdf.set_text_color(51, 65, 85)
    if buyer:
        pdf.cell(50, 8, txt="Name:", border=0)
        pdf.cell(0, 8, txt=buyer.full_name, border=0, ln=1)
        pdf.cell(50, 8, txt="Email:", border=0)
        pdf.cell(0, 8, txt=buyer.email, border=0, ln=1)
        pdf.cell(50, 8, txt="Phone:", border=0)
        pdf.cell(0, 8, txt=buyer.phone_number or "N/A", border=0, ln=1)
    else:
        pdf.cell(0, 8, txt="No client specified in this transaction.", border=0, ln=1)
    
    pdf.output(filename)
    return filename

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
    if prop.status != "pending_sold":
        raise HTTPException(status_code=400, detail="Property is not pending a sale approval")
    
    prop.status = "sold"
    pdf_path = generate_transaction_report(db, prop, "Sale")
    db.commit()

    # [RESTORE] Notify Admins of finalized transaction
    admins = db.query(models.User).filter(models.User.role == "admin").all()
    for admin in admins:
        if admin.email:
            background_tasks.add_task(
                email.send_admin_report_email,
                admin_email=admin.email,
                admin_name=admin.full_name,
                property_title=prop.title,
                tx_type="Sale",
                pdf_path=pdf_path
            )

    return {"message": "Sale approved. Property is now marked as sold and report generated."}

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
    
    prop.status = "rented"
    pdf_path = generate_transaction_report(db, prop, "Rent")
    db.commit()

    # [RESTORE] Notify Admins of finalized transaction
    admins = db.query(models.User).filter(models.User.role == "admin").all()
    for admin in admins:
        if admin.email:
            background_tasks.add_task(
                email.send_admin_report_email,
                admin_email=admin.email,
                admin_name=admin.full_name,
                property_title=prop.title,
                tx_type="Rent",
                pdf_path=pdf_path
            )

    return {"message": "Rent approved. Property is now marked as rented and report generated."}

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
    return [{"name": f} for f in os.listdir("reports") if f.endswith(".pdf")]

@router.get("/admin/reports/{filename}")
def download_report(filename: str, current_user: models.User = Depends(auth.RoleChecker(["admin"]))):
    """Downloads a specific transaction report."""
    file_path = os.path.join("reports", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(file_path, filename=filename)

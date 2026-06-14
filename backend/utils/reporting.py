from datetime import datetime
import os, tempfile, models
from fpdf import FPDF
from services import email

def generate_transaction_report(db, prop, tx_type, save_path=None):
    """Professional PDF report generation using fpdf2."""
    if not save_path:
        # If no path provided, we'll save to a temporary location
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        temp_dir = tempfile.gettempdir()
        save_path = os.path.join(temp_dir, f"Transaction_Prop{prop.id}_{tx_type}_{timestamp}.pdf")
    
    agent = db.query(models.User).filter(models.User.id == prop.agent_id).first() if prop.agent_id else None
    owner = db.query(models.User).filter(models.User.id == prop.owner_id).first() if prop.owner_id else None
    buyer = db.query(models.User).filter(models.User.id == prop.buyer_id).first() if prop.buyer_id else None
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Colors
    PRIMARY = (30, 41, 59)    # Slate 800
    SECONDARY = (71, 85, 105) # Slate 600
    ACCENT = (37, 99, 235)    # Blue 600
    BG_LIGHT = (248, 250, 252)# Slate 50
    
    # 1. HEADER
    pdf.set_fill_color(*ACCENT)
    pdf.rect(0, 0, 210, 40, "F")
    
    pdf.set_xy(15, 12)
    pdf.set_font("helvetica", "B", 24)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 10, "ELITE ESTATE", ln=True)
    
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 5, "PROFESSIONAL REAL ESTATE AUTOMATION", ln=True)
    
    # Transaction Badge
    pdf.set_xy(150, 15)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_text_color(*ACCENT)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(45, 10, f"{tx_type.upper()}", border=0, ln=True, align="C", fill=True)
    
    pdf.set_xy(15, 45)
    pdf.set_text_color(*SECONDARY)
    pdf.set_font("helvetica", "I", 9)
    pdf.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="R")
    pdf.ln(5)

    # Helper function for section headers
    def section_header(title):
        pdf.set_fill_color(*BG_LIGHT)
        pdf.set_text_color(*PRIMARY)
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(0, 10, f"  {title}", ln=True, fill=True)
        pdf.set_draw_color(*ACCENT)
        pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
        pdf.ln(3)

    # 2. PROPERTY DETAILS
    section_header("PROPERTY INFORMATION")
    
    prop_data = [
        ("Property ID", str(prop.id)),
        ("Title", prop.title),
        ("Type", prop.property_type.value.capitalize() if hasattr(prop.property_type, 'value') else str(prop.property_type)),
        ("Area", f"{prop.area} sqm" if prop.area else "N/A"),
        ("Rooms", f"{prop.bedrooms} Bed / {prop.bathrooms} Bath"),
        ("City/State", f"{prop.city}, {prop.state or ''}"),
        ("Country", prop.country)
    ]
    
    pdf.set_font("helvetica", "", 11)
    with pdf.table(col_widths=(40, 150), borders_layout="NONE", line_height=7) as table:
        for label, value in prop_data:
            row = table.row()
            pdf.set_font("helvetica", "B", 10)
            row.cell(f"{label}:")
            pdf.set_font("helvetica", "", 10)
            row.cell(value)
    
    pdf.ln(5)

    # 3. FINANCIAL SUMMARY
    section_header("FINANCIAL SUMMARY")
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(*ACCENT)
    pdf.cell(40, 10, "Total Price:", ln=0)
    pdf.cell(0, 10, f"{prop.price:,} {prop.currency}", ln=1)
    
    if tx_type == "Rent" and prop.rent_start_date:
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(*PRIMARY)
        pdf.cell(40, 8, "Period:", ln=0)
        pdf.set_font("helvetica", "", 11)
        pdf.cell(0, 8, f"{prop.rent_start_date.strftime('%b %d, %Y')} to {prop.rent_end_date.strftime('%b %d, %Y')}", ln=1)
    
    pdf.ln(5)

    # 4. PARTIES INVOLVED
    section_header("PARTICIPANTS & CONTACTS")
    
    participants = [
        ("Role", "Name", "Email", "Phone"),
        ("Listing Owner", owner.full_name if owner else "N/A", owner.email if owner else "N/A", owner.phone_number if owner else "N/A"),
        ("Assigned Agent", agent.full_name if agent else "N/A", agent.email if agent else "N/A", agent.phone_number if agent else "N/A"),
        ("Buyer/Tenant", buyer.full_name if buyer else "N/A", buyer.email if buyer else "N/A", buyer.phone_number if buyer else "N/A")
    ]
    
    pdf.set_font("helvetica", "", 9)
    with pdf.table(borders_layout="HORIZONTAL_LINES", line_height=8) as table:
        for i, (role, name, email_val, phone) in enumerate(participants):
            row = table.row()
            if i == 0:
                pdf.set_font("helvetica", "B", 9)
                pdf.set_fill_color(241, 245, 249)
            else:
                pdf.set_font("helvetica", "", 9)
            row.cell(role)
            row.cell(name)
            row.cell(email_val)
            row.cell(phone)

    # Footer
    pdf.set_y(-25)
    pdf.set_font("helvetica", "I", 8)
    pdf.set_text_color(148, 163, 184)
    pdf.cell(0, 10, "This is an electronically generated document by Elite Estate Automation System.", align="C", ln=True)
    pdf.cell(0, 5, f"Page {pdf.page_no()}", align="C")

    pdf.output(save_path)
    return save_path

def finalize_transaction(db, prop, tx_type, background_tasks):
    """Unified logic to finalize a sale or rent transaction."""
    # 1. Update Property Status
    prop.status = "sold" if tx_type == "Sale" else "rented"
    
    # 2. Update associated visit status to 'finished'
    buyer_telegram_chat_id = None
    if prop.buyer_id:
        buyer = db.query(models.User).filter(models.User.id == prop.buyer_id).first()
        if buyer:
            buyer_telegram_chat_id = buyer.telegram_chat_id

    visit = db.query(models.Visit).filter(
        models.Visit.property_id == prop.id,
        (models.Visit.client_id == prop.buyer_id) | 
        ((models.Visit.telegram_chat_id == buyer_telegram_chat_id) & (models.Visit.telegram_chat_id.isnot(None))),
        models.Visit.status == "scheduled"
    ).order_by(models.Visit.visit_date.desc()).first()
    if visit:
        visit.status = "finished"

    # 3. Create Report Record
    new_report = models.Report(
        property_id=prop.id,
        transaction_type=tx_type,
        buyer_id=prop.buyer_id,
        agent_id=prop.agent_id,
        price_at_time=prop.price
    )
    db.add(new_report)
    db.commit()

    # 4. Generate temporary PDF for notification email
    pdf_path = generate_transaction_report(db, prop, tx_type)
    
    # 5. Notify Admins
    admins = db.query(models.User).filter(models.User.role == "admin").all()
    for admin in admins:
        if admin.email:
            background_tasks.add_task(
                email.send_admin_report_email,
                admin_email=admin.email,
                admin_name=admin.full_name,
                property_title=prop.title,
                tx_type=tx_type,
                pdf_path=pdf_path
            )
            
    # 6. Notify Client
    buyer = db.query(models.User).filter(models.User.id == prop.buyer_id).first() if prop.buyer_id else None
    if buyer and buyer.email:
        background_tasks.add_task(
            email.send_client_transaction_success_email,
            client_email=buyer.email,
            client_name=buyer.full_name,
            property_title=prop.title,
            tx_type=tx_type,
            property_price=f"{prop.price:,} {prop.currency}",
            property_location=f"{prop.city}, {prop.country}"
        )
    
    return new_report

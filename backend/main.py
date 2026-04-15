from fastapi import FastAPI, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
import models, schemas, database, auth, ai_utils, cloud_storage
import email_utils
from fpdf import FPDF
from utils import embeddings

def log_debug(msg):
    with open("/app/upload_debug.log", "a") as f:
        f.write(f"{datetime.now()}: {msg}\n")
    print(msg, flush=True)
from datetime import timedelta, timezone
from typing import List, Optional
import os
import shutil
from uuid import uuid4
from fastapi import UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from imagekitio import ImageKit
import base64

# Create the database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Real Estate Automation API",
    description="Backend API for the AI-Driven Real Estate Automation Platform",
    version="1.0.0"
)
# ImageKit is now handled in cloud_storage.py

# Configure CORS make it more secure
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for property images (seeded)
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# --- Authentication Routes ---

@app.post("/auth/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """
    Creates a new user account.
    Passwords are automatically hashed before being saved.
    """
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password and create user object
    hashed_pwd = auth.get_password_hash(user.password)
    new_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_pwd,
        role=user.role,
        manager_id=user.manager_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    """
    Standard OAuth2 Login flow.
    Returns a JWT access_token valid for 30 minutes.
    """
    # Verify user exists
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account has been deactivated. Please contact your manager.",
        )
    
    # Generate the JWT token
    access_token = auth.create_access_token(data={"sub": user.email, "role": user.role, "user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.put("/auth/profile", response_model=schemas.User)
def update_profile(
    user_update: schemas.UserUpdate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Updates the authenticated user's profile information."""
    if user_update.full_name:
        current_user.full_name = user_update.full_name
    if user_update.email:
        # Check if new email is already taken
        if current_user.email != user_update.email:
            existing = db.query(models.User).filter(models.User.email == user_update.email).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = user_update.email
    if user_update.phone_number:
        current_user.phone_number = user_update.phone_number
    if user_update.google_calendar_id:
        current_user.google_calendar_id = user_update.google_calendar_id
        
    db.commit()
    db.refresh(current_user)
    return current_user

@app.get("/agents/{agent_id}/calendar")
def get_agent_calendar(agent_id: int, db: Session = Depends(database.get_db)):
    """Returns the Google Calendar ID for a specific agent."""
    agent = db.query(models.User).filter(models.User.id == agent_id, models.User.role == "agent").first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    return {
        "agent_id": agent.id,
        "full_name": agent.full_name,
        "email": agent.email,  # <--- ADD THIS LINE
        "google_calendar_id": agent.google_calendar_id
    }

@app.put("/auth/password")
def update_password(
    passwords: schemas.PasswordUpdate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Securely updates the authenticated user's password."""
    if not auth.verify_password(passwords.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    current_user.hashed_password = auth.get_password_hash(passwords.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

# --- Visit & Reminder Management ---

@app.post("/visits/book", response_model=schemas.VisitResponse)
def book_visit(
    payload: schemas.VisitCreate,
    db: Session = Depends(database.get_db)
):
    """Called by n8n after a Google Calendar event is successfully created."""
    
    # FIX: Explicitly convert the incoming time to UTC before saving
    visit_date_utc = payload.visit_date.astimezone(timezone.utc)
    
    new_visit = models.Visit(
        property_id=payload.property_id,
        client_id=None,
        agent_id=payload.agent_id,
        visit_date=visit_date_utc, # Save the UTC version
        telegram_chat_id=payload.client_telegram_id,
        status="scheduled",
        reminder_sent=False
    )
    db.add(new_visit)
    db.commit()
    db.refresh(new_visit)
    return new_visit

@app.get("/visits/upcoming", response_model=List[schemas.VisitResponse])
def get_upcoming_visits(
    db: Session = Depends(database.get_db)
):
    """Returns visits scheduled within the next window that haven't been notified yet."""
    # Use Naive UTC to match TIMESTAMP columns in PostgreSQL
    now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
    
    window_start = now_naive
    window_end = now_naive + timedelta(minutes=60)
    
    print(f"🔍 DEBUG: Current Time (Naive UTC): {now_naive}")
    print(f"🔍 DEBUG: Window: {window_start} to {window_end}")
    
    visits = db.query(models.Visit).filter(
        models.Visit.status == 'scheduled',
        models.Visit.reminder_sent == False,
        models.Visit.visit_date >= window_start,
        models.Visit.visit_date <= window_end
    ).all()
    
    # Detailed Debugging
    if not visits:
        all_scheduled = db.query(models.Visit).filter(models.Visit.status == 'scheduled', models.Visit.reminder_sent == False).order_by(models.Visit.visit_date.asc()).all()
        print(f"⚠️ DEBUG: No visits in window. Found {len(all_scheduled)} total scheduled/pending-reminder visits:")
        for v in all_scheduled:
            print(f"  - Visit ID {v.id}: {v.visit_date} (Naive: {v.visit_date.tzinfo is None})")
    else:
        print(f"✅ DEBUG: Found {len(visits)} visits in window.")
        for v in visits:
            print(f"  - Match: Visit ID {v.id} at {v.visit_date}")
            
    return visits

@app.put("/visits/{visit_id}/reminder-sent")
def mark_reminder_sent(
    visit_id: int,
    db: Session = Depends(database.get_db)
):
    """Marks a visit as notified so reminders don't send twice."""
    visit = db.query(models.Visit).filter(models.Visit.id == visit_id).first()
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    visit.reminder_sent = True
    db.commit()
    return {"message": "Reminder marked as sent"}

# --- Basic Health & Testing ---

@app.get("/")
async def root():
    return {"status": "online", "message": "Welcome to the API"}

@app.get("/auth/me", response_model=schemas.User)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    """
    Test endpoint to verify the JWT token works.
    Only accessible if a valid token is provided in the header.
    """
    return current_user
#property Routes for Head Agent
@app.post("/properties", response_model=schemas.Property, status_code=status.HTTP_201_CREATED)
def create_property(
    property_in: schemas.PropertyCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Allows Head Agents to list a new property related to their agency."""
    db_property = db.query(models.Property).filter(models.Property.slug == property_in.slug).first()
    if db_property:
        raise HTTPException(status_code=400, detail="Slug already exists")
    
    # Create the property object
    new_property = models.Property(
        **property_in.dict(exclude={"feature_ids", "agent_id", "owner_id"}),
        owner_id=property_in.owner_id or current_user.id,
        agent_id=property_in.agent_id
    )
    
    # Add features if provided
    if property_in.feature_ids:
        features = db.query(models.Feature).filter(models.Feature.id.in_(property_in.feature_ids)).all()
        new_property.features = features
    
    # Generate embedding for description
    new_property.description_vector = embeddings.get_embedding(new_property.description)
    
    # Save the property
    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    return new_property

@app.put("/properties/{property_id}/assign")
def assign_property_to_agent(
    property_id: int,
    payload: dict,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Allows Head Agents or Admins to assign a property to a Sub-Agent."""
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
        
    # Validation: only owners or admins can assign
    if current_user.role != "admin" and prop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to assign this property")
        
    prop.agent_id = payload.get("agent_id")
    db.commit()
    return {"message": "Agent assigned successfully"}

@app.delete("/properties/{property_id}")
def delete_property(
    property_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Deletes a property listing. Only owner or admin can perform this."""
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
        
    if current_user.role != "admin" and prop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this property")
        
    db.delete(prop)
    db.commit()
    return {"message": "Property deleted successfully"}

@app.put("/properties/{property_id}", response_model=schemas.Property)
def update_property(
    property_id: int,
    property_in: schemas.PropertyUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["admin", "head_agent"]))
):
    """Updates property details. Only owners or admins can perform this."""
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
        
    if current_user.role != "admin" and prop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this property")
        
    update_data = property_in.dict(exclude_unset=True, exclude={"feature_ids"})
    
    # Check if description is being updated
    description_changed = "description" in update_data and update_data["description"] != prop.description
    
    for key, value in update_data.items():
        setattr(prop, key, value)
        
    if description_changed:
        prop.description_vector = embeddings.get_embedding(prop.description)
        
    if property_in.feature_ids is not None:
        features = db.query(models.Feature).filter(models.Feature.id.in_(property_in.feature_ids)).all()
        prop.features = features
        
    db.commit()
    db.refresh(prop)
    return prop

@app.get("/agency/staff", response_model=List[schemas.User])
def get_team_staff(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Returns Sub-Agents managed by the Head Agent."""
    if current_user.role == "admin":
        return db.query(models.User).filter(models.User.role == "agent").all()
    return db.query(models.User).filter(
        models.User.manager_id == current_user.id,
        models.User.role == "agent"
    ).all()

@app.get("/agency/properties", response_model=List[schemas.Property])
def get_agency_properties(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Returns all properties for agency management. Head Agents only see their own listings (all statuses)."""
    query = db.query(models.Property).options(
        joinedload(models.Property.images),
        joinedload(models.Property.features),
        joinedload(models.Property.owner),
        joinedload(models.Property.agent)
    )
    
    if current_user.role == "admin":
        return query.all()
        
    return query.filter(models.Property.owner_id == current_user.id).all()

@app.patch("/agency/staff/{agent_id}/toggle-status")
def toggle_sub_agent_status(
    agent_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Head Agent can enable/disable their own sub-agents."""
    agent = db.query(models.User).filter(models.User.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    # Head agents can only toggle their own subordinates
    if current_user.role == "head_agent" and agent.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only manage your own sub-agents")
    
    agent.is_active = not agent.is_active
    db.commit()

    # Send status update email
    if agent.email:
        background_tasks.add_task(
            email_utils.send_account_status_email,
            user_email=agent.email,
            user_name=agent.full_name,
            is_active=agent.is_active,
            manager_name=current_user.full_name
        )

    return {"message": f"Agent {'enabled' if agent.is_active else 'disabled'}", "is_active": agent.is_active}

def generate_transaction_report(db, prop, tx_type):
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/Transaction_Prop{prop.id}_{tx_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    agent = db.query(models.User).get(prop.agent_id) if prop.agent_id else None
    owner = db.query(models.User).get(prop.owner_id) if prop.owner_id else None
    buyer = db.query(models.User).get(prop.buyer_id) if prop.buyer_id else None
    
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
    pdf.cell(50, 8, text="Property ID:", border=0)
    pdf.cell(0, 8, text=str(prop.id), border=0, ln=1)
    
    pdf.cell(50, 8, text="Title:", border=0)
    pdf.multi_cell(0, 8, text=prop.title, border=0, align="L")
    
    pdf.cell(50, 8, text="Location:", border=0)
    pdf.cell(0, 8, text=f"{prop.city}, {prop.country}", border=0, ln=1)
    
    pdf.cell(50, 8, text="Price:", border=0)
    pdf.cell(0, 8, text=f"{prop.price} {prop.currency}", border=0, ln=1)
    
    if tx_type == "Rent" and prop.rent_start_date:
        pdf.cell(50, 8, text="Rent Duration:", border=0)
        pdf.cell(0, 8, text=f"{prop.rent_start_date.strftime('%Y-%m-%d')} to {prop.rent_end_date.strftime('%Y-%m-%d')}", border=0, ln=1)
    pdf.ln(10)
    
    # Staff Section
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 10, text="STAFF DETAILS", ln=True)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
    pdf.ln(2)
    
    pdf.set_font("helvetica", "", 12)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(50, 8, text="Head Agent:", border=0)
    pdf.cell(0, 8, text=f"{owner.full_name if owner else 'None'} ({owner.email if owner else 'N/A'})", border=0, ln=1)
    
    pdf.cell(50, 8, text="Sub Agent:", border=0)
    pdf.cell(0, 8, text=f"{agent.full_name if agent else 'None'} ({agent.email if agent else 'N/A'})", border=0, ln=1)
    pdf.ln(10)
    
    # Client Section
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 10, text="CLIENT / BUYER DETAILS", ln=True)
    pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
    pdf.ln(2)
    
    pdf.set_font("helvetica", "", 12)
    pdf.set_text_color(51, 65, 85)
    if buyer:
        pdf.cell(50, 8, text="Name:", border=0)
        pdf.cell(0, 8, text=buyer.full_name, border=0, ln=1)
        pdf.cell(50, 8, text="Email:", border=0)
        pdf.cell(0, 8, text=buyer.email, border=0, ln=1)
        pdf.cell(50, 8, text="Phone:", border=0)
        pdf.cell(0, 8, text=buyer.phone_number or "N/A", border=0, ln=1)
    else:
        pdf.cell(0, 8, text="No client specified in this transaction.", border=0, ln=1)
    
    pdf.output(filename)
    return filename

@app.post("/agency/properties/{property_id}/approve-sale")
def approve_property_sale(
    property_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Head Agent approves a sub-agent's sale request, marking the property as officially sold."""
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if current_user.role == "head_agent" and prop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only approve sales for your own properties")
    if prop.status != "pending_sold":
        raise HTTPException(status_code=400, detail="Property is not pending a sale approval")
    
    prop.status = "sold"
    pdf_path = generate_transaction_report(db, prop, "Sale")
    
    # Notify all Admins
    admins = db.query(models.User).filter(models.User.role == "admin").all()
    for admin in admins:
        if admin.email:
            background_tasks.add_task(
                email_utils.send_admin_report_email,
                admin_email=admin.email,
                admin_name=admin.full_name,
                property_title=prop.title,
                tx_type="Sale",
                pdf_path=pdf_path
            )
            
    db.commit()
    return {"message": "Sale approved. Property is now marked as sold and notification sent to Admin."}

@app.post("/agency/properties/{property_id}/reject-sale")
def reject_property_sale(
    property_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Head Agent rejects a sub-agent's sale request, reverting property to available."""
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if current_user.role == "head_agent" and prop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    prop.status = "available"
    db.commit()
    return {"message": "Sale rejected. Property reverted to available."}

@app.post("/agency/properties/{property_id}/approve-rent")
def approve_property_rent(
    property_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Head Agent approves a sub-agent's rent request, marking the property as rented."""
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if current_user.role == "head_agent" and prop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only approve rents for your own properties")
    if prop.status != "pending_rent":
        raise HTTPException(status_code=400, detail="Property is not pending a rent approval")
        
    prop.status = "rented"
    pdf_path = generate_transaction_report(db, prop, "Rent")
    
    # Notify all Admins
    admins = db.query(models.User).filter(models.User.role == "admin").all()
    for admin in admins:
        if admin.email:
            background_tasks.add_task(
                email_utils.send_admin_report_email,
                admin_email=admin.email,
                admin_name=admin.full_name,
                property_title=prop.title,
                tx_type="Rent",
                pdf_path=pdf_path
            )
            
    db.commit()
    return {"message": "Rent approved. Property is now marked as rented and notification sent to Admin."}

@app.post("/agency/properties/{property_id}/reject-rent")
def reject_property_rent(
    property_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Head Agent rejects a sub-agent's rent request, reverting property to available."""
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


@app.get("/agency/clients", response_model=List[schemas.User])
def get_clients(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """Returns all registered clients to select from."""
    return db.query(models.User).filter(models.User.role == "client").all()

# --- Sub-Agent Operations ---

@app.get("/agent/inquiries")
def get_agent_inquiries(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """Returns visits/inquiries for the currently logged-in sub-agent, formatted as leads."""
    if current_user.role == "admin":
        visits = db.query(models.Visit).order_by(models.Visit.created_at.desc()).all()
    elif current_user.role == "head_agent":
        # Head agents see all visits on properties they own
        visits = db.query(models.Visit).join(
            models.Property, models.Visit.property_id == models.Property.id
        ).filter(
            models.Property.owner_id == current_user.id
        ).order_by(models.Visit.created_at.desc()).all()
    else:
        visits = db.query(models.Visit).filter(
            models.Visit.agent_id == current_user.id
        ).order_by(models.Visit.created_at.desc()).all()

    # Format as inquiry-like objects for the frontend
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
    
    # Also add pending_sold/pending_rent properties as alert notifications for head_agents
    if current_user.role in ["head_agent", "admin"]:
        pending_props = db.query(models.Property).filter(
            models.Property.status.in_(["pending_sold", "pending_rent"]),
            models.Property.owner_id == current_user.id if current_user.role == "head_agent" else True
        ).all()
        for p in pending_props:
            agent = db.query(models.User).filter(models.User.id == p.agent_id).first() if p.agent_id else None
            buyer = db.query(models.User).filter(models.User.id == p.buyer_id).first() if p.buyer_id else None
            # Only add if not already in result
            if not any(r["property_id"] == p.id for r in result):
                req_type = "Sale" if p.status == "pending_sold" else "Rent"
                status_display = "sold" if p.status == "pending_sold" else "rented"
                
                msg = f"Sub-Agent {agent.full_name if agent else 'unknown'} is requesting approval to mark this property as {status_display}."
                if buyer:
                    msg += f" Client Email: {buyer.email}."
                if p.status == "pending_rent" and p.rent_start_date and p.rent_end_date:
                    msg += f" Duration: {p.rent_start_date.strftime('%b %d, %Y')} to {p.rent_end_date.strftime('%b %d, %Y')}."
                
                result.insert(0, {
                    "id": -p.id,  # negative id to differentiate
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

@app.put("/agent/inquiries/{inquiry_id}/status")
def update_inquiry_status(
    inquiry_id: int,
    status: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """Update visit/inquiry status. Maps to visit status."""
    vis = db.query(models.Visit).filter(models.Visit.id == inquiry_id).first()
    if not vis:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    # Map inquiry status back to visit status
    status_map = {"new": "scheduled", "replied": "finished", "closed": "cancelled"}
    vis.status = status_map.get(status, status)
    db.commit()
    return {"message": "Status updated"}

@app.get("/agent/visits", response_model=List[schemas.VisitDetailResponse])
def get_agent_visits(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """Fetches visits scheduled for this agent or agency properties."""
    query = db.query(models.Visit).options(
        joinedload(models.Visit.property),
        joinedload(models.Visit.client)
    )
    
    if current_user.role == "admin":
        return query.all()
        
    return query.filter(models.Visit.agent_id == current_user.id).order_by(models.Visit.visit_date.asc()).all()

@app.put("/agent/visits/{visit_id}/status")
def update_visit_status(
    visit_id: int,
    status: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """Updates a visit (e.g. 'scheduled' -> 'finished')."""
    vis = db.query(models.Visit).filter(models.Visit.id == visit_id).first()
    if not vis:
        raise HTTPException(status_code=404, detail="Visit not found")
        
    vis.status = status
    db.commit()
    return {"message": "Visit status updated"}

@app.patch("/properties/{property_id}/status")
def update_property_status(
    property_id: int,
    payload: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """Allows agents to update property status (e.g., mark as sold/pending)."""
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    
    new_status = payload.get("status")
    if new_status not in ["available", "sold", "pending_sold", "rented", "pending_rent"]:
        raise HTTPException(status_code=400, detail="Invalid status value")
    
    prop.status = new_status
    if new_status == "pending_rent":
        if "rent_start_date" in payload and payload["rent_start_date"]:
            prop.rent_start_date = datetime.fromisoformat(payload["rent_start_date"].replace("Z", "+00:00"))
        if "rent_end_date" in payload and payload["rent_end_date"]:
            prop.rent_end_date = datetime.fromisoformat(payload["rent_end_date"].replace("Z", "+00:00"))
            
    if new_status in ["pending_sold", "pending_rent"]:
        if "buyer_id" in payload and payload["buyer_id"]:
            prop.buyer_id = payload["buyer_id"]
            
    db.commit()

    # --- Email Notification to Head Agent ---
    if new_status in ["pending_sold", "pending_rent"]:
        head_agent = db.query(models.User).filter(models.User.id == prop.owner_id).first()
        buyer = db.query(models.User).filter(models.User.id == prop.buyer_id).first() if prop.buyer_id else None

        if head_agent and head_agent.email:
            tx_type = "Sale" if new_status == "pending_sold" else "Rent"
            rent_start_str = prop.rent_start_date.strftime("%Y-%m-%d") if prop.rent_start_date else None
            rent_end_str = prop.rent_end_date.strftime("%Y-%m-%d") if prop.rent_end_date else None

            background_tasks.add_task(
                email_utils.send_transaction_request_email,
                head_agent_email=head_agent.email,
                head_agent_name=head_agent.full_name,
                sub_agent_name=current_user.full_name,
                sub_agent_email=current_user.email,
                property_title=prop.title,
                property_location=f"{prop.city}, {prop.country}",
                property_price=f"{prop.price} {prop.currency}",
                tx_type=tx_type,
                client_email=buyer.email if buyer else None,
                rent_start=rent_start_str,
                rent_end=rent_end_str,
            )

    return {"message": f"Property status updated to {new_status}"}

@app.get("/properties", response_model=List[schemas.Property])
def list_properties(db: Session = Depends(database.get_db)):
    """Publicly lists all available properties with images and features."""
    return db.query(models.Property).options(
        joinedload(models.Property.images),
        joinedload(models.Property.features)
    ).filter(models.Property.status == "available").all()
# --- Admin View ---

@app.get("/admin/reports")
def list_reports(current_user: models.User = Depends(auth.RoleChecker(["admin"]))):
    """Returns a list of available transaction reports."""
    if not os.path.exists("reports"):
        return []
    return [{"name": f} for f in os.listdir("reports") if f.endswith(".pdf")]

@app.get("/admin/reports/{filename}")
def download_report(filename: str, current_user: models.User = Depends(auth.RoleChecker(["admin"]))):
    """Downloads a specific transaction report."""
    file_path = os.path.join("reports", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(file_path, filename=filename)
@app.get("/admin/properties", response_model=List[schemas.Property])
def admin_view_all_properties(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["admin"]))
):
    """Administrator access to view every property on the platform."""
    return db.query(models.Property).all()

@app.get("/admin/head_agents", response_model=List[schemas.User])
def get_head_agents(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["admin"]))
):
    """Returns all Head Agents for selection/assignment."""
    return db.query(models.User).filter(models.User.role == "head_agent").all()


@app.get("/admin/users", response_model=List[schemas.User])
def get_all_users(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["admin"]))
):
    """Admin access to view all registered staff users (excludes visitors who self-registered)."""
    return db.query(models.User).filter(models.User.role != "visitor").all()

@app.post("/admin/users", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user_admin(
    user_in: schemas.UserCreateAdmin,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["admin", "head_agent"]))
):
    """Admin access to directly create staff accounts (e.g. Head Agents). Head Agents can also create Agents."""
    db_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_pwd = auth.get_password_hash(user_in.password)
    new_user = models.User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_pwd,
        role=user_in.role,
        phone_number=user_in.phone_number,
        manager_id=user_in.manager_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.patch("/admin/users/{user_id}/toggle-status")
def toggle_user_status(
    user_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["admin"]))
):
    """Admin endpoint to enable or disable a user account."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot disable your own account")
    
    user.is_active = not user.is_active
    db.commit()

    # Send status update email
    if user.email:
        background_tasks.add_task(
            email_utils.send_account_status_email,
            user_email=user.email,
            user_name=user.full_name,
            is_active=user.is_active,
            manager_name=current_user.full_name
        )

    return {"message": f"User {'enabled' if user.is_active else 'disabled'} successfully", "is_active": user.is_active}

# --- Features (Amenities) ---
@app.get("/features", response_model=List[schemas.Feature])
def list_features(db: Session = Depends(database.get_db)):
    """Returns all available amenity/feature tags for property listings."""
    return db.query(models.Feature).order_by(models.Feature.name).all()

@app.post("/features", response_model=schemas.Feature, status_code=status.HTTP_201_CREATED)
def create_feature(
    feature: schemas.FeatureBase,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["admin"]))
):
    """Admin endpoint to create a new amenity/feature tag."""
    existing = db.query(models.Feature).filter(models.Feature.name == feature.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Feature already exists")
    new_feature = models.Feature(name=feature.name)
    db.add(new_feature)
    db.commit()
    db.refresh(new_feature)
    return new_feature



# --- AI & Semantic Search Routes ---

@app.post("/search/semantic", response_model=List[schemas.Property])
@app.get("/search/semantic", response_model=List[schemas.Property])
def semantic_search(
    query: Optional[str] = None,
    location: Optional[str] = None,
    property_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_price: Optional[str] = None,
    feature_ids: Optional[List[int]] = Query(None),
    payload: Optional[schemas.SemanticSearchQuery] = None,
    db: Session = Depends(database.get_db)
):
    """
    Performs keyword-based search AND filtered search by features.
    """
    search_text = payload.query if (payload and payload.query) else query
    selected_features = payload.feature_ids if (payload and payload.feature_ids) else feature_ids
    
    # Base query
    q = db.query(models.Property).options(
        joinedload(models.Property.images),
        joinedload(models.Property.features)
    ).filter(models.Property.status == 'available')

    # 1. Apply Standard Filters
    if location:
        q = q.filter(models.Property.city.ilike(f"%{location}%"))
    if property_type and property_type.lower() != 'all':
        q = q.filter(models.Property.property_type == property_type.lower())
    if min_price:
        q = q.filter(models.Property.price >= min_price)
    if max_price:
        q = q.filter(models.Property.price <= max_price)

    # 2. Keyword Search (Replace Semantic)
    if search_text:
        # Search in title OR description
        q = q.filter(
            (models.Property.title.ilike(f"%{search_text}%")) | 
            (models.Property.description.ilike(f"%{search_text}%"))
        )
    
    # 3. Filter by Features (Must have ALL selected features)
    if selected_features:
        for fid in selected_features:
            q = q.filter(models.Property.features.any(models.Feature.id == fid))

    # 4. Apply Sorting
    if sort_price == 'asc':
        q = q.order_by(models.Property.price.asc())
    elif sort_price == 'desc':
        q = q.order_by(models.Property.price.desc())
    else:
        q = q.order_by(models.Property.created_at.desc())

    return q.limit(40).all()

@app.post("/search/rag", response_model=schemas.RAGSearchResponse)
def rag_search(
    payload: schemas.SemanticSearchQuery,
    db: Session = Depends(database.get_db)
):
    """
    Enhanced keyword search for RAG systems (replaces vector-based retrieval).
    """
    search_text = payload.query
    
    q = db.query(models.Property).options(
        joinedload(models.Property.features)
    ).filter(models.Property.status == 'available')
    
    if search_text:
        q = q.filter(
            (models.Property.title.ilike(f"%{search_text}%")) | 
            (models.Property.description.ilike(f"%{search_text}%"))
        )
    
    if payload.feature_ids:
        for fid in payload.feature_ids:
            q = q.filter(models.Property.features.any(models.Feature.id == fid))
            
    results = q.limit(10).all()
    
    if not results:
        return {"context": "No properties found matching this search.", "properties": []}
        
    rag_properties = []
    context_parts = []
    
    for i, prop in enumerate(results):
        # Format google_maps_url if coords exist
        maps_url = None
        if prop.latitude and prop.longitude:
            maps_url = f"https://maps.google.com/?q={prop.latitude},{prop.longitude}"
            
        # Create RAGProperty object
        features_list = [f.name for f in prop.features]
        agent_name = prop.agent.full_name if prop.agent else "Not Assigned"
        rag_prop = schemas.RAGProperty(
            id=prop.id,
            agent_id=prop.agent_id,
            agent_name = agent_name,
            title=prop.title,
            property_type=prop.property_type,
            listing_type=prop.listing_type,
            price=prop.price,
            currency=prop.currency,
            city=prop.city,
            area=prop.area,
            bedrooms=prop.bedrooms,
            bathrooms=prop.bathrooms,
            features=features_list,
            description=prop.description,
            latitude=prop.latitude,
            longitude=prop.longitude,
            google_maps_url=maps_url,
            agent_calendar_id=prop.agent.google_calendar_id if prop.agent else None
        )
        rag_properties.append(rag_prop)
        

        # Build context string
        context_parts.append(
            f"Property ID: {prop.id}\n"
            f"Title: {prop.title}\n"
            f"Type: {prop.property_type.capitalize()} for {prop.listing_type.capitalize()}\n"
            f"Price: {prop.price:,.0f} {prop.currency}\n"
            f"Location: {prop.city}, {prop.country}\n"
            f"Area: {prop.area}m²\n"
            f"Bedrooms: {prop.bedrooms} | Bathrooms: {prop.bathrooms}\n"
            f"Features: {', '.join(features_list)}\n"
            f"Description: {prop.description}\n"
            f"Assigned Agent: {agent_name} (ID: {prop.agent_id})"
        )
        
    return {
        "context": "\n\n".join(context_parts),
        "properties": rag_properties
    }
# --- AI Assistant (RAG Pipeline Entry) ---
@app.post("/properties/{property_id}/ask", response_model=schemas.AIResponse)
def ask_ai_about_property(
    property_id: int, 
    payload: schemas.PropertyQuestion,
    db: Session = Depends(database.get_db)
):
    """Entry point for the RAG-powered Property Assistant."""
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Context retrieval for RAG
    # We combine title, description, and features for a rich context
    features_list = [f.name for f in prop.features]
    context = f"""
    Title: {prop.title}
    Type: {prop.property_type} ({prop.listing_type})
    Price: {prop.price} {prop.currency}
    Description: {prop.description}
    Amenities: {", ".join(features_list)}
    Location: {prop.city}, {prop.country}
    Structure: {prop.bedrooms} beds, {prop.bathrooms} baths
    """
    
    answer = ai_utils.ask_property_assistant(payload.question, context)
    
    return {
        "answer": answer,
        "source_confidence": 0.95
    }
@app.post("/properties/{property_id}/images", response_model=List[schemas.PropertyImage])
async def upload_property_images(
    property_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Uploads multiple images for a specific property."""
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Check ownership (Admin can do anything)
    if current_user.role != "admin" and prop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't own this property")
    log_debug(f"📥 Received {len(files)} files for property {property_id}")
    uploaded_images = []
    
    for file in files:
        log_debug(f"🚀 Processing file: {file.filename}")
        # Use our new cloud storage utility
        image_url = await cloud_storage.upload_to_imagekit(file, file.filename)
        
        if image_url:
            log_debug(f"✅ Image URL received: {image_url}")
            # Create DB record
            is_primary = (len(prop.images) == 0 and len(uploaded_images) == 0)
            
            db_image = models.PropertyImage(
                property_id=property_id,
                image_url=image_url,
                is_primary=is_primary
            )
            db.add(db_image)
            uploaded_images.append(db_image)
        else:
            log_debug(f"⚠️ Skipping DB record for failed upload: {file.filename}")

    db.commit()
    log_debug(f"🏁 Final result: {len(uploaded_images)} images saved to DB.")
    return uploaded_images

@app.get("/properties/{property_id}/images", response_model=List[schemas.PropertyImage])
def get_property_images(property_id: int, db: Session = Depends(database.get_db)):
    """Returns all images for a specific property."""
    log_debug(f"🔍 GET /properties/{property_id}/images called")
    
    # Check if property exists first
    prop_exists = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop_exists:
        log_debug(f"❌ Property {property_id} not found in DB")
        raise HTTPException(status_code=404, detail="Property not found")
        
    # Query images directly
    images = db.query(models.PropertyImage).filter(models.PropertyImage.property_id == property_id).all()
    log_debug(f"✅ Found {len(images)} images for property {property_id} (Direct query)")
    
    for img in images:
        log_debug(f"  - Image ID: {img.id}, URL: {img.image_url}")
        
    return images
@app.get("/properties/{property_id}/map")
def get_property_map(property_id: int, db: Session = Depends(database.get_db)):
    """Returns Google Maps URL for a property."""
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if not prop.latitude or not prop.longitude:
        raise HTTPException(status_code=404, detail="No coordinates available for this property")
    
    maps_url = f"https://maps.google.com/?q={prop.latitude},{prop.longitude}"
    return {
        "latitude": float(prop.latitude),
        "longitude": float(prop.longitude),
        "google_maps_url": maps_url
    }
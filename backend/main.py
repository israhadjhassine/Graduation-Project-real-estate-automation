from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import models, schemas, database, auth, ai_utils
from datetime import timedelta
from typing import List, Optional
import os
import shutil
from uuid import uuid4
from fastapi import UploadFile, File
from fastapi.staticfiles import StaticFiles

# Create the database tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Real Estate Automation API",
    description="Backend API for the AI-Driven Real Estate Automation Platform",
    version="1.0.0"
)
os.makedirs("static/uploads/properties", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
# Configure CORS make it more secure
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        
    db.commit()
    db.refresh(current_user)
    return current_user

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
    # Save the property without vector embedding for now
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
    for key, value in update_data.items():
        setattr(prop, key, value)
        
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
    """Returns all properties for agency management. Head Agents can assign any property."""
    return db.query(models.Property).all()


# --- Sub-Agent Operations ---
@app.get("/agent/inquiries", response_model=List[schemas.InquiryResponse])
def get_agent_inquiries(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """Fetches inquiries linked to the properties assigned to the agent or agency."""
    if current_user.role == "admin":
        return db.query(models.Inquiry).all()
        
    # Find all properties assigned to this agent
    agent_properties = db.query(models.Property.id).filter(models.Property.agent_id == current_user.id).subquery()
    
    return db.query(models.Inquiry).filter(
        models.Inquiry.property_id.in_(agent_properties)
    ).order_by(models.Inquiry.created_at.desc()).all()

@app.put("/agent/inquiries/{inquiry_id}/status")
def update_inquiry_status(
    inquiry_id: int,
    status: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """Updates the status of an inquiry (e.g. 'new' -> 'replied')."""
    inq = db.query(models.Inquiry).filter(models.Inquiry.id == inquiry_id).first()
    if not inq:
        raise HTTPException(status_code=404, detail="Inquiry not found")
        
    # Verify permission (simplified: assuming inter-agency trust for now)
    inq.status = status
    db.commit()
    return {"message": "Status updated successfully"}

@app.get("/agent/visits", response_model=List[schemas.VisitResponse])
def get_agent_visits(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """Fetches visits scheduled for this agent or agency properties."""
    if current_user.role == "admin":
        return db.query(models.Visit).all()
        
    return db.query(models.Visit).filter(models.Visit.agent_id == current_user.id).order_by(models.Visit.visit_date.asc()).all()

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

@app.get("/properties", response_model=List[schemas.Property])
def list_properties(db: Session = Depends(database.get_db)):
    """Publicly lists all available properties."""
    return db.query(models.Property).filter(models.Property.status == "available").all()
# --- Admin View ---
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
    """Admin access to view all users."""
    return db.query(models.User).all()

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



# --- AI & Semantic Search Routes ---

@app.get("/search/semantic", response_model=List[schemas.Property])
def semantic_search(
    query: Optional[str] = None,
    location: Optional[str] = None,
    property_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_price: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    """
    Performs basic text search and complex filtering.
    """
    query_obj = db.query(models.Property).filter(models.Property.status == "available")
    
    if query:
        query_obj = query_obj.filter(
            (models.Property.title.ilike(f"%{query}%")) | (models.Property.description.ilike(f"%{query}%"))
        )
    
    if location:
        query_obj = query_obj.filter(models.Property.city.ilike(f"%{location}%"))
        
    if property_type and property_type.lower() != "all":
        query_obj = query_obj.filter(models.Property.property_type.ilike(f"%{property_type}%"))
        
    if min_price is not None:
        query_obj = query_obj.filter(models.Property.price >= min_price)
        
    if max_price is not None:
        query_obj = query_obj.filter(models.Property.price <= max_price)
        
    if sort_price:
        if sort_price.lower() == 'asc':
            query_obj = query_obj.order_by(models.Property.price.asc())
        elif sort_price.lower() == 'desc':
            query_obj = query_obj.order_by(models.Property.price.desc())
            
    return query_obj.all()
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
    uploaded_images = []
    
    for file in files:
        # Generate unique filename
        file_ext = file.filename.split(".")[-1]
        file_name = f"{uuid4()}.{file_ext}"
        file_path = f"static/uploads/properties/{file_name}"
        
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create DB record
        # Note: First image uploaded becomes primary automatically
        is_primary = len(prop.images) == 0 and len(uploaded_images) == 0
        
        db_image = models.PropertyImage(
            property_id=property_id,
            image_url=f"/static/uploads/properties/{file_name}",
            is_primary=is_primary
        )
        db.add(db_image)
        uploaded_images.append(db_image)
    db.commit()
    return uploaded_images
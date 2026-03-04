from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import models, schemas, database, auth, ai_utils
from datetime import timedelta
from typing import List
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
        agency_id=user.agency_id
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
        **property_in.dict(exclude={"feature_ids"}),
        agency_id=current_user.agency_id,
        owner_id=current_user.id
    )
    
    # Add features if provided
    if property_in.feature_ids:
        features = db.query(models.Feature).filter(models.Feature.id.in_(property_in.feature_ids)).all()
        new_property.features = features
    # AI Vectorization: Automatically generate vector from description
    new_property.description_vector = ai_utils.get_embedding(property_in.description)

    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    return new_property
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

# --- AI & Semantic Search Routes ---

@app.get("/search/semantic", response_model=List[schemas.Property])
def semantic_search(query: str, db: Session = Depends(database.get_db)):
    """
    Performs AI Semantic Search using pgvector Cosine Similarity (<=>).
    """
    if not query:
        return db.query(models.Property).filter(models.Property.status == "available").all()
    
    # 1. Convert user query to vector
    query_vector = ai_utils.get_query_embedding(query)
    
    if not query_vector:
        # Fallback to normal title search if AI fails
        return db.query(models.Property).filter(
            models.Property.title.ilike(f"%{query}%"),
            models.Property.status == "available"
        ).all()

    # 2. Perform Cosine Similarity search in PostgreSQL
    # pgvector operator <=> is Cosine Distance (1 - Cosine Similarity)
    # We order by distance ascending (top matches first)
    results = db.query(models.Property).filter(
        models.Property.status == "available"
    ).order_by(
        models.Property.description_vector.cosine_distance(query_vector)
    ).limit(10).all()

    return results
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
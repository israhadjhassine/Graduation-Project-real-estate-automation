from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from typing import List, Optional
import models, schemas, database, auth
from services import ai, storage, email

router = APIRouter(
    tags=["Properties"]
)

@router.get("/properties", response_model=List[schemas.Property])
def list_properties(db: Session = Depends(database.get_db)):
    """Publicly lists all available properties with images and features."""
    return db.query(models.Property).options(
        joinedload(models.Property.images),
        joinedload(models.Property.features)
    ).filter(models.Property.status == "available").all()

@router.post("/properties", response_model=schemas.Property, status_code=status.HTTP_201_CREATED)
def create_property(
    property_in: schemas.PropertyCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Allows Head Agents to list a new property related to their agency."""
    db_property = db.query(models.Property).filter(models.Property.slug == property_in.slug).first()
    if db_property:
        raise HTTPException(status_code=400, detail="Slug already exists")
    
    new_property = models.Property(
        **property_in.dict(exclude={"feature_ids", "agent_id", "owner_id"}),
        owner_id=property_in.owner_id or current_user.id,
        agent_id=property_in.agent_id
    )
    
    if property_in.feature_ids:
        features = db.query(models.Feature).filter(models.Feature.id.in_(property_in.feature_ids)).all()
        new_property.features = features
    new_property.description_vector = ai.get_embedding(new_property.description)
    
    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    return new_property

@router.get("/properties/{property_id}", response_model=schemas.Property)
def get_property_detail(property_id: int, db: Session = Depends(database.get_db)):
    """Returns full details for a single property."""
    prop = db.query(models.Property).options(
        joinedload(models.Property.images),
        joinedload(models.Property.features),
        joinedload(models.Property.owner),
        joinedload(models.Property.agent)
    ).filter(models.Property.id == property_id).first()
    
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop

@router.put("/properties/{property_id}", response_model=schemas.Property)
def update_property(
    property_id: int,
    property_in: schemas.PropertyUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["admin", "head_agent"]))
):
    """Updates property details. Only owners or admins can perform this."""
    prop = db.query(models.Property).options(joinedload(models.Property.owner)).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
        
    # Authorization: Admin, Owner, or the Manager of the Owner
    is_admin = current_user.role == "admin"
    is_owner = prop.owner_id == current_user.id
    is_manager = current_user.role == "head_agent" and prop.owner and prop.owner.manager_id == current_user.id
        
    if not (is_admin or is_owner or is_manager):
        raise HTTPException(status_code=403, detail="Not authorized to edit this property")
        
    update_data = property_in.dict(exclude_unset=True, exclude={"feature_ids"})
    
    # Check if description changed for AI re-embedding
    description_changed = "description" in update_data and update_data["description"] != prop.description
    
    # Apply updates
    for key, value in update_data.items():
        setattr(prop, key, value)
    
    if description_changed:
        prop.description_vector = ai.get_embedding(prop.description)
        
    if property_in.feature_ids is not None:
        features = db.query(models.Feature).filter(models.Feature.id.in_(property_in.feature_ids)).all()
        prop.features = features
        
    db.commit()
    db.refresh(prop)
    return prop

@router.delete("/properties/{property_id}")
def delete_property(
    property_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Deletes a property listing. Only owner or admin can perform this."""
    prop = db.query(models.Property).options(joinedload(models.Property.owner)).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
        
    # Authorization: Admin, Owner, or the Manager of the Owner
    is_admin = current_user.role == "admin"
    is_owner = prop.owner_id == current_user.id
    is_manager = current_user.role == "head_agent" and prop.owner and prop.owner.manager_id == current_user.id
        
    if not (is_admin or is_owner or is_manager):
        raise HTTPException(status_code=403, detail="Not authorized to delete this property")
        
    db.delete(prop)
    db.commit()
    return {"message": "Property deleted successfully"}

@router.put("/properties/{property_id}/assign")
def assign_property_to_agent(
    property_id: int,
    payload: dict,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Allows Head Agents or Admins to assign a property to a Sub-Agent."""
    prop = db.query(models.Property).options(joinedload(models.Property.owner)).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
        
    # Authorization: Admin, Owner, or the Manager of the Owner
    is_admin = current_user.role == "admin"
    is_owner = prop.owner_id == current_user.id
    is_manager = current_user.role == "head_agent" and prop.owner and prop.owner.manager_id == current_user.id
        
    if not (is_admin or is_owner or is_manager):
        raise HTTPException(status_code=403, detail="Not authorized to assign this property")
        
    prop.agent_id = payload.get("agent_id")
    db.commit()
    return {"message": "Agent assigned successfully"}

from utils.reporting import finalize_transaction

@router.patch("/properties/{property_id}/status")
def update_property_status(
    property_id: int,
    payload: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """Allows owners/admins to update property status. Sold/Rented finalizes immediately."""
    prop = db.query(models.Property).options(joinedload(models.Property.owner)).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Authorization
    is_admin = current_user.role == "admin"
    is_owner = prop.owner_id == current_user.id
    is_manager = current_user.role == "head_agent" and prop.owner and prop.owner.manager_id == current_user.id
    is_assigned = prop.agent_id == current_user.id
    
    new_status = payload.get("status")
    
    # If trying to finalize (sold/rented), must be admin/owner/manager
    if new_status in ["sold", "rented"]:
        if not (is_admin or is_owner or is_manager):
            raise HTTPException(status_code=403, detail="Only owners or admins can finalize transactions directly.")
    else:
        # For other statuses (available, pending_*), allow assigned agent too
        if not (is_admin or is_owner or is_manager or is_assigned):
            raise HTTPException(status_code=403, detail="You are not authorized to update this property status")
    
    if new_status not in ["available", "sold", "rented", "pending_sold", "pending_rent"]:
        raise HTTPException(status_code=400, detail="Invalid status value")
    
    if new_status == "rented":
        if "rent_start_date" in payload and payload["rent_start_date"]:
            prop.rent_start_date = datetime.fromisoformat(payload["rent_start_date"].replace("Z", "+00:00"))
        if "rent_end_date" in payload and payload["rent_end_date"]:
            prop.rent_end_date = datetime.fromisoformat(payload["rent_end_date"].replace("Z", "+00:00"))
            
    if new_status in ["sold", "rented"]:
        if "buyer_id" in payload and payload["buyer_id"]:
            prop.buyer_id = payload["buyer_id"]
        
        tx_type = "Sale" if new_status == "sold" else "Rent"
        finalize_transaction(db, prop, tx_type, background_tasks)
        return {"message": f"Transaction finalized as {tx_type}. Report generated."}
            
    prop.status = new_status
    db.commit()
    return {"message": f"Property status updated to {new_status}"}

@router.post("/properties/{property_id}/request-transaction")
def request_property_transaction(
    property_id: int,
    request_in: schemas.TransactionRequestCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """Allows Sub-Agents to request a sale/rent approval from their Head Agent."""
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Verify agent is assigned to this property or is the owner
    if prop.agent_id != current_user.id and prop.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not assigned to this property")

    # Check if a pending request already exists
    existing = db.query(models.TransactionRequest).filter(
        models.TransactionRequest.property_id == property_id,
        models.TransactionRequest.status == "pending"
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="A pending transaction request already exists for this property")

    new_request = models.TransactionRequest(
        property_id=property_id,
        agent_id=current_user.id,
        client_id=request_in.client_id,
        type=request_in.type,
        price=request_in.price,
        rent_start_date=request_in.rent_start_date,
        rent_end_date=request_in.rent_end_date,
        status="pending"
    )
    db.add(new_request)

    # Update property status to show 'Pending' in UI
    prop.status = "pending_sold" if request_in.type == "Sale" else "pending_rent"
    
    db.commit()
    return {"message": "Transaction request submitted for head agent approval."}

@router.post("/properties/{property_id}/images", response_model=List[schemas.PropertyImage])
async def upload_property_images(
    property_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Allows uploading multiple images at once for a property."""
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
        
    uploaded_images = []
    for file in files:
        res = await storage.upload_to_imagekit(file, file.filename)
        if not res:
            continue
            
        has_primary = db.query(models.PropertyImage).filter(
            models.PropertyImage.property_id == property_id, 
            models.PropertyImage.is_primary == True
        ).first() is not None
        
        is_primary = (not has_primary and len(uploaded_images) == 0)
        db_image = models.PropertyImage(
            property_id=property_id,
            image_url=res["url"],
            file_id=res["file_id"],
            is_primary=is_primary
        )
        db.add(db_image)
        uploaded_images.append(db_image)
    
    db.commit()
    for img in uploaded_images:
        db.refresh(img)
    return uploaded_images

@router.delete("/properties/images/{image_id}")
def delete_property_image(
    image_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Deletes a property image from DB and ImageKit."""
    image = db.query(models.PropertyImage).filter(models.PropertyImage.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
        
    prop = db.query(models.Property).options(joinedload(models.Property.owner)).filter(models.Property.id == image.property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
        
    is_admin = current_user.role == "admin"
    is_owner = prop.owner_id == current_user.id
    is_manager = current_user.role == "head_agent" and prop.owner and prop.owner.manager_id == current_user.id
        
    if not (is_admin or is_owner or is_manager):
        raise HTTPException(status_code=403, detail="Not authorized to delete images from this property")
        
    if image.file_id:
        storage.delete_from_imagekit(image.file_id)
        
    was_primary = image.is_primary
    prop_id = image.property_id
    
    db.delete(image)
    db.commit()

    if was_primary:
        next_image = db.query(models.PropertyImage).filter(models.PropertyImage.property_id == prop_id).first()
        if next_image:
            next_image.is_primary = True
            db.commit()
            
    return {"message": "Image deleted successfully"}

@router.get("/properties/{property_id}/map")
def get_property_map(property_id: int, db: Session = Depends(database.get_db)):
    """Returns Google Maps coordinates for a property."""
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    if not prop.latitude or not prop.longitude:
        raise HTTPException(status_code=404, detail="No coordinates available")
    
    return {
        "latitude": float(prop.latitude),
        "longitude": float(prop.longitude),
        "google_maps_url": f"https://maps.google.com/?q={prop.latitude},{prop.longitude}"
    }

@router.post("/properties/{property_id}/ask", response_model=schemas.AIResponse)
def ask_ai_about_property(
    property_id: int, 
    payload: schemas.PropertyQuestion,
    db: Session = Depends(database.get_db)
):
    """Entry point for the RAG-powered Property Assistant."""
    prop = db.query(models.Property).filter(models.Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    
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
    
    answer = ai.ask_property_assistant(payload.question, context)
    return {"answer": answer, "source_confidence": 0.95}

@router.api_route("/search/semantic", methods=["GET", "POST"], response_model=List[schemas.Property])
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
    """Strict Semantic Search - No keyword fallback."""
    search_text = payload.query if (payload and payload.query) else query
    
    q = db.query(models.Property).options(
        joinedload(models.Property.images),
        joinedload(models.Property.features)
    ).filter(models.Property.status == 'available')

    if location:
        q = q.filter(models.Property.city.ilike(f"%{location}%"))
    if property_type and property_type.lower() != 'all':
        q = q.filter(models.Property.property_type == property_type.lower())
    if min_price:
        q = q.filter(models.Property.price >= min_price)
    if max_price:
        q = q.filter(models.Property.price <= max_price)
        
    if search_text:
        query_embedding = ai.get_query_embedding(search_text)
        if not query_embedding:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                detail="Semantic search service (Ollama) is temporarily unavailable."
            )
        
        # Strict rank by semantic similarity
        q = q.order_by(models.Property.description_vector.l2_distance(query_embedding))
    else:
        if sort_price == 'asc':
            q = q.order_by(models.Property.price.asc())
        elif sort_price == 'desc':
            q = q.order_by(models.Property.price.desc())
        else:
            q = q.order_by(models.Property.created_at.desc())

    return q.limit(40).all()

@router.post("/search/rag", response_model=schemas.RAGSearchResponse)
def rag_search(
    payload: schemas.SemanticSearchQuery,
    db: Session = Depends(database.get_db)
):
    """RAG search - Strict Semantic context preparation."""
    search_text = payload.query
    q = db.query(models.Property).options(joinedload(models.Property.features)).filter(models.Property.status == 'available')
    
    if search_text:
        query_embedding = ai.get_query_embedding(search_text)
        if not query_embedding:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                detail="RAG search service (Ollama) is temporarily unavailable."
            )
            
        q = q.order_by(models.Property.description_vector.l2_distance(query_embedding))
            
    if payload.feature_ids:
        for fid in payload.feature_ids:
            q = q.filter(models.Property.features.any(models.Feature.id == fid))
            
    results = q.limit(10).all()
    if not results:
        return {"context": "No properties found matching this search.", "properties": []}
        
    rag_properties = []
    context_parts = []
    for prop in results:
        maps_url = f"https://maps.google.com/?q={prop.latitude},{prop.longitude}" if prop.latitude and prop.longitude else None
        features_list = [f.name for f in prop.features]
        agent_name = prop.agent.full_name if prop.agent else "Not Assigned"
        rag_prop = schemas.RAGProperty(
            id=prop.id, agent_id=prop.agent_id, agent_name=agent_name, title=prop.title,
            property_type=prop.property_type, listing_type=prop.listing_type, price=prop.price,
            currency=prop.currency, city=prop.city, area=prop.area, bedrooms=prop.bedrooms,
            bathrooms=prop.bathrooms, features=features_list, description=prop.description,
            latitude=prop.latitude, longitude=prop.longitude, google_maps_url=maps_url,
            agent_calendar_id=prop.agent.google_calendar_id if prop.agent else None
        )
        rag_properties.append(rag_prop)
        context_parts.append(
            f"Property ID: {prop.id}\nTitle: {prop.title}\nType: {prop.property_type} for {prop.listing_type}\n"
            f"Price: {prop.price:,.0f} {prop.currency}\nLocation: {prop.city}, {prop.country}\n"
            f"Assigned Agent: {agent_name}"
        )
        
    return {"context": "\n\n".join(context_parts), "properties": rag_properties}

@router.get("/agent/properties", response_model=List[schemas.Property])
def get_agent_properties(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """Returns properties assigned to the current agent, regardless of status."""
    return db.query(models.Property).options(
        joinedload(models.Property.images), joinedload(models.Property.features),
        joinedload(models.Property.owner), joinedload(models.Property.agent)
    ).filter(models.Property.agent_id == current_user.id).all()

@router.get("/agency/properties", response_model=List[schemas.Property])
def get_agency_properties(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Returns all properties for agency management (Admin sees all, Head Agent sees owned)."""
    query = db.query(models.Property).options(
        joinedload(models.Property.images), joinedload(models.Property.features),
        joinedload(models.Property.owner), joinedload(models.Property.agent)
    )
    if current_user.role == "admin":
        return query.all()
    return query.filter(models.Property.owner_id == current_user.id).all()

@router.get("/features", response_model=List[schemas.Feature])
def list_features(db: Session = Depends(database.get_db)):
    """Returns all available amenity/feature tags."""
    return db.query(models.Feature).order_by(models.Feature.name).all()

@router.post("/features", response_model=schemas.Feature, status_code=status.HTTP_201_CREATED)
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

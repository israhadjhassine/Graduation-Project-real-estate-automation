from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from typing import List, Optional
import models, schemas, database, auth
from repositories import PropertyRepository
from services import ai, storage, email

router = APIRouter(
    tags=["Properties"]
)

@router.get("/properties", response_model=List[schemas.Property])
def list_properties(db: Session = Depends(database.get_db)):
    """Publicly lists all available properties with images and features."""
    return PropertyRepository.get_all_available(db)

@router.post("/properties", response_model=schemas.Property, status_code=status.HTTP_201_CREATED)
def create_property(
    property_in: schemas.PropertyCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Allows Head Agents to list a new property related to their agency."""
    if PropertyRepository.get_by_slug(db, property_in.slug):
        raise HTTPException(status_code=400, detail="Slug already exists")
    
    new_property = models.Property(
        **property_in.dict(exclude={"feature_ids", "agent_id", "owner_id"}),
        owner_id=property_in.owner_id or current_user.id,
        agent_id=property_in.agent_id
    )
    
    if property_in.feature_ids:
        new_property.features = PropertyRepository.get_features_by_ids(db, property_in.feature_ids)
    
    new_property.description_vector = ai.get_embedding(new_property.description)
    return PropertyRepository.save(db, new_property)

@router.get("/properties/{property_id}", response_model=schemas.Property)
def get_property_detail(property_id: int, db: Session = Depends(database.get_db)):
    """Returns full details for a single property."""
    prop = PropertyRepository.get_by_id(db, property_id)
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
    prop = PropertyRepository.get_by_id(db, property_id)
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
        prop.features = PropertyRepository.get_features_by_ids(db, property_in.feature_ids)
        
    PropertyRepository.commit(db)
    PropertyRepository.refresh(db, prop)
    return prop

@router.delete("/properties/{property_id}")
def delete_property(
    property_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Deletes a property listing. Only owner or admin can perform this."""
    prop = PropertyRepository.get_by_id(db, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
        
    # Authorization: Admin, Owner, or the Manager of the Owner
    is_admin = current_user.role == "admin"
    is_owner = prop.owner_id == current_user.id
    is_manager = current_user.role == "head_agent" and prop.owner and prop.owner.manager_id == current_user.id
        
    if not (is_admin or is_owner or is_manager):
        raise HTTPException(status_code=403, detail="Not authorized to delete this property")
        
    PropertyRepository.delete(db, prop)
    return {"message": "Property deleted successfully"}

@router.put("/properties/{property_id}/assign")
def assign_property_to_agent(
    property_id: int,
    payload: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Allows Head Agents or Admins to assign a property to a Sub-Agent."""
    prop = PropertyRepository.get_by_id(db, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
        
    # Authorization: Admin, Owner, or the Manager of the Owner
    is_admin = current_user.role == "admin"
    is_owner = prop.owner_id == current_user.id
    is_manager = current_user.role == "head_agent" and prop.owner and prop.owner.manager_id == current_user.id
        
    if not (is_admin or is_owner or is_manager):
        raise HTTPException(status_code=403, detail="Not authorized to assign this property")
        
    agent_id = payload.get("agent_id")
    prop.agent_id = agent_id
    PropertyRepository.commit(db)

    # Trigger Email Notification to Sub-Agent
    if agent_id:
        agent = db.query(models.User).filter(models.User.id == agent_id).first()
        if agent and agent.email:
            location = f"{prop.city}, {prop.country}"
            background_tasks.add_task(
                email.send_property_assignment_email,
                agent_email=agent.email,
                agent_name=agent.full_name,
                property_title=prop.title,
                property_location=location,
                head_agent_name=current_user.full_name
            )

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
    prop = PropertyRepository.get_by_id(db, property_id)
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
    
    if new_status not in ["available", "sold", "rented", "pending_sold", "pending_rent", "approved_sold", "approved_rent"]:
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
    prop = PropertyRepository.get_by_id(db, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    
    # Verify agent is assigned to this property or is the owner
    if prop.agent_id != current_user.id and prop.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not assigned to this property")

    # Check if a pending or approved request already exists
    existing = db.query(models.TransactionRequest).filter(
        models.TransactionRequest.property_id == property_id,
        models.TransactionRequest.status.in_(["pending", "approved"])
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="An active transaction request already exists for this property")

    # Check if there is a visit for this property, client, and agent with status "finished"
    visit = db.query(models.Visit).filter(
        models.Visit.property_id == property_id,
        models.Visit.client_id == request_in.client_id,
        models.Visit.agent_id == current_user.id,
        models.Visit.status == "finished"
    ).first()
    if not visit:
        raise HTTPException(
            status_code=400,
            detail="You must have a completed (finished) visit with this client for this property before requesting a transaction."
        )

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
    PropertyRepository.add_transaction_request(db, new_request)

    # Update property status to show 'Pending' in UI
    prop.status = "pending_sold" if request_in.type == "Sale" else "pending_rent"
    
    PropertyRepository.commit(db)
    return {"message": "Transaction request submitted for head agent approval."}

@router.post("/properties/{property_id}/finalize-transaction")
def finalize_property_transaction(
    property_id: int,
    payload: schemas.TransactionFinalize,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["agent", "head_agent", "admin"]))
):
    """Allows Sub-Agents to finalize (complete or cancel) an approved transaction request."""
    prop = PropertyRepository.get_by_id(db, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
        
    # Verify agent is assigned to this property, is the owner, or is admin
    if prop.agent_id != current_user.id and prop.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to finalize this transaction")

    # Find the approved transaction request for this property
    req = db.query(models.TransactionRequest).filter(
        models.TransactionRequest.property_id == property_id,
        models.TransactionRequest.status == "approved"
    ).first()
    if not req:
        raise HTTPException(status_code=400, detail="No approved transaction request found for this property")

    if payload.action == "complete":
        # Finalize the transaction
        req.status = "completed"
        prop.buyer_id = req.client_id
        if req.type == "Rent":
            prop.rent_start_date = req.rent_start_date
            prop.rent_end_date = req.rent_end_date
            
        # Cancel all other scheduled visits for this property
        db.query(models.Visit).filter(
            models.Visit.property_id == property_id,
            models.Visit.status == "scheduled"
        ).update({"status": "cancelled"})
            
        # Call finalize_transaction (which sets prop.status, creates report, sends emails)
        finalize_transaction(db, prop, req.type, background_tasks)
        db.commit()
        return {"message": f"Transaction completed successfully. Property status set to {prop.status}."}
        
    elif payload.action == "cancel":
        # Revert request and property status
        req.status = "cancelled"
        prop.status = "available"
        db.commit()
        return {"message": "Transaction request cancelled. Property is now available."}
        
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Must be 'complete' or 'cancel'.")

@router.post("/properties/{property_id}/images", response_model=List[schemas.PropertyImage])
async def upload_property_images(
    property_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Allows uploading multiple images at once for a property."""
    prop = PropertyRepository.get_by_id(db, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
        
    uploaded_images = []
    for file in files:
        res = await storage.upload_to_imagekit(file, file.filename)
        if not res:
            continue
            
        has_primary = PropertyRepository.has_primary_image(db, property_id)
        
        is_primary = (not has_primary and len(uploaded_images) == 0)
        db_image = models.PropertyImage(
            property_id=property_id,
            image_url=res["url"],
            file_id=res["file_id"],
            is_primary=is_primary
        )
        PropertyRepository.add_image(db, db_image)
        uploaded_images.append(db_image)
    
    PropertyRepository.commit(db)
    for img in uploaded_images:
        PropertyRepository.refresh(db, img)
    return uploaded_images

@router.delete("/properties/images/{image_id}")
def delete_property_image(
    image_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Deletes a property image from DB and ImageKit."""
    image = PropertyRepository.get_image_by_id(db, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
        
    prop = PropertyRepository.get_by_id(db, image.property_id)
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
    
    PropertyRepository.delete(db, image)
    PropertyRepository.commit(db)

    if was_primary:
        next_image = PropertyRepository.get_first_image(db, prop_id)
        if next_image:
            next_image.is_primary = True
            PropertyRepository.commit(db)
            
    return {"message": "Image deleted successfully"}

@router.get("/properties/{property_id}/map")
def get_property_map(property_id: int, db: Session = Depends(database.get_db)):
    """Returns Google Maps coordinates for a property."""
    prop = PropertyRepository.get_by_id(db, property_id)
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
    prop = PropertyRepository.get_by_id(db, property_id)
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
    f_ids = payload.feature_ids if (payload and payload.feature_ids) else feature_ids
    
    q = PropertyRepository.get_query(db).options(
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
    if f_ids:
        for fid in f_ids:
            q = q.filter(models.Property.features.any(models.Feature.id == fid))
        
    if search_text:
        from sqlalchemy import or_
        q = q.filter(
            or_(
                models.Property.title.ilike(f"%{search_text}%"),
                models.Property.description.ilike(f"%{search_text}%")
            )
        )
        
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
    q = PropertyRepository.get_query(db).options(joinedload(models.Property.features)).filter(models.Property.status == 'available')
    
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
            id=prop.id, 
            agent_id=prop.agent_id, 
            agent_name=agent_name, 
            title=prop.title,
            property_type=prop.property_type, 
            listing_type=prop.listing_type, 
            price=prop.price,
            currency=prop.currency, 
            city=prop.city, area=prop.area, 
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
    return PropertyRepository.get_all_for_agent(db, current_user.id)

@router.get("/agency/properties", response_model=List[schemas.Property])
def get_agency_properties(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Returns all properties for agency management (Admin sees all, Head Agent sees owned)."""
    if current_user.role == "admin":
        return PropertyRepository.get_all_for_agency(db)
    return PropertyRepository.get_all_for_agency(db, owner_id=current_user.id)

@router.get("/features", response_model=List[schemas.Feature])
def list_features(db: Session = Depends(database.get_db)):
    """Returns all available amenity/feature tags."""
    return PropertyRepository.list_features(db)

@router.post("/features", response_model=schemas.Feature, status_code=status.HTTP_201_CREATED)
def create_feature(
    feature: schemas.FeatureBase,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["admin"]))
):
    """Admin endpoint to create a new amenity/feature tag."""
    existing = PropertyRepository.get_feature_by_name(db, feature.name)
    if existing:
        raise HTTPException(status_code=400, detail="Feature already exists")
    new_feature = models.Feature(name=feature.name)
    return PropertyRepository.save_feature(db, new_feature)

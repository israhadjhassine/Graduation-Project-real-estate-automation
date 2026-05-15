from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Any
import models

class PropertyRepository:
    @staticmethod
    def get_all_available(db: Session) -> List[models.Property]:
        return db.query(models.Property).options(
            joinedload(models.Property.images),
            joinedload(models.Property.features)
        ).filter(models.Property.status == "available").all()

    @staticmethod
    def get_by_id(db: Session, property_id: int) -> Optional[models.Property]:
        return db.query(models.Property).options(
            joinedload(models.Property.images),
            joinedload(models.Property.features),
            joinedload(models.Property.owner),
            joinedload(models.Property.agent)
        ).filter(models.Property.id == property_id).first()

    @staticmethod
    def get_by_slug(db: Session, slug: str) -> Optional[models.Property]:
        return db.query(models.Property).filter(models.Property.slug == slug).first()

    @staticmethod
    def get_features_by_ids(db: Session, feature_ids: List[int]) -> List[models.Feature]:
        return db.query(models.Feature).filter(models.Feature.id.in_(feature_ids)).all()

    @staticmethod
    def save(db: Session, db_obj: models.Property) -> models.Property:
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def commit(db: Session):
        db.commit()

    @staticmethod
    def delete(db: Session, db_obj: models.Property):
        db.delete(db_obj)
        db.commit()

    @staticmethod
    def get_all_for_agent(db: Session, agent_id: int) -> List[models.Property]:
        return db.query(models.Property).options(
            joinedload(models.Property.images),
            joinedload(models.Property.features),
            joinedload(models.Property.owner),
            joinedload(models.Property.agent)
        ).filter(models.Property.agent_id == agent_id).all()

    @staticmethod
    def get_all_for_agency(db: Session, owner_id: int = None) -> List[models.Property]:
        query = db.query(models.Property).options(
            joinedload(models.Property.images),
            joinedload(models.Property.features),
            joinedload(models.Property.owner),
            joinedload(models.Property.agent)
        )
        if owner_id:
            query = query.filter(models.Property.owner_id == owner_id)
        return query.all()

    @staticmethod
    def list_features(db: Session) -> List[models.Feature]:
        return db.query(models.Feature).order_by(models.Feature.name).all()

    @staticmethod
    def get_feature_by_name(db: Session, name: str) -> Optional[models.Feature]:
        return db.query(models.Feature).filter(models.Feature.name == name).first()

    @staticmethod
    def save_feature(db: Session, feature: models.Feature) -> models.Feature:
        db.add(feature)
        db.commit()
        db.refresh(feature)
        return feature

    @staticmethod
    def get_image_by_id(db: Session, image_id: int) -> Optional[models.PropertyImage]:
        return db.query(models.PropertyImage).filter(models.PropertyImage.id == image_id).first()

    @staticmethod
    def has_primary_image(db: Session, property_id: int) -> bool:
        return db.query(models.PropertyImage).filter(
            models.PropertyImage.property_id == property_id,
            models.PropertyImage.is_primary == True
        ).first() is not None

    @staticmethod
    def add_image(db: Session, image: models.PropertyImage) -> models.PropertyImage:
        db.add(image)
        return image

    @staticmethod
    def get_pending_transaction_request(db: Session, property_id: int) -> Optional[models.TransactionRequest]:
        return db.query(models.TransactionRequest).filter(
            models.TransactionRequest.property_id == property_id,
            models.TransactionRequest.status == "pending"
        ).first()

    @staticmethod
    def add_transaction_request(db: Session, request: models.TransactionRequest) -> models.TransactionRequest:
        db.add(request)
        return request

    @staticmethod
    def get_first_image(db: Session, property_id: int) -> Optional[models.PropertyImage]:
        return db.query(models.PropertyImage).filter(models.PropertyImage.property_id == property_id).first()

    @staticmethod
    def refresh(db: Session, obj: Any):
        db.refresh(obj)

    @staticmethod
    def get_query(db: Session):
        """Returns a base query for custom filtering if needed by the router."""
        return db.query(models.Property)

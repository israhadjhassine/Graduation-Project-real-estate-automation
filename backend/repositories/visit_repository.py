from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
import models

class VisitRepository:
    @staticmethod
    def save(db: Session, visit: models.Visit) -> models.Visit:
        db.add(visit)
        db.commit()
        db.refresh(visit)
        return visit

    @staticmethod
    def get_upcoming(db: Session, window_start: datetime, window_end: datetime) -> List[models.Visit]:
        return db.query(models.Visit).filter(
            models.Visit.status == 'scheduled',
            models.Visit.reminder_sent == False,
            models.Visit.visit_date >= window_start,
            models.Visit.visit_date <= window_end
        ).all()

    @staticmethod
    def get_by_id(db: Session, visit_id: int) -> Optional[models.Visit]:
        return db.query(models.Visit).filter(models.Visit.id == visit_id).first()

    @staticmethod
    def get_with_property_and_owner(db: Session, visit_id: int) -> Optional[models.Visit]:
        return db.query(models.Visit).options(
            joinedload(models.Visit.property).joinedload(models.Property.owner)
        ).filter(models.Visit.id == visit_id).first()

    @staticmethod
    def get_all_detailed(db: Session, agent_ids: Optional[List[int]] = None) -> List[models.Visit]:
        query = db.query(models.Visit).options(
            joinedload(models.Visit.property),
            joinedload(models.Visit.client),
            joinedload(models.Visit.agent)
        )
        if agent_ids is not None:
            query = query.filter(models.Visit.agent_id.in_(agent_ids))
        
        return query.order_by(models.Visit.visit_date.asc()).all()

    @staticmethod
    def list_clients(db: Session) -> List[models.User]:
        return db.query(models.User).filter(models.User.role == "client").all()

    @staticmethod
    def commit(db: Session):
        db.commit()

    @staticmethod
    def find_scheduled_visit(
        db:Session,
        telegram_chat_id:str,
        property_id:int,
        visit_date:datetime,
    )->Optional[models.Visit]:
        return db.query(models.Visit).filter(
            models.Visit.telegram_chat_id ==telegram_chat_id,
            models.Visit.property_id == property_id,
            models.Visit.visit_date == visit_date,
            models.Visit.status == "scheduled", 
        ).first()
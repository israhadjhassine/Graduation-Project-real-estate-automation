from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import models

class InquiryRepository:
    @staticmethod
    def get_pending_detailed(db: Session, agent_id: Optional[int] = None, sub_agent_ids: Optional[List[int]] = None, owner_id: Optional[int] = None) -> List[models.TransactionRequest]:
        query = db.query(models.TransactionRequest).options(
            joinedload(models.TransactionRequest.property),
            joinedload(models.TransactionRequest.agent),
            joinedload(models.TransactionRequest.client)
        ).filter(models.TransactionRequest.status == "pending")

        if owner_id:
            # For Head Agents: their properties OR their team's requests
            query = query.join(models.TransactionRequest.property).filter(
                (models.Property.owner_id == owner_id) | 
                (models.TransactionRequest.agent_id.in_(sub_agent_ids or []))
            )
        elif agent_id:
            # For Agents: only their own
            query = query.filter(models.TransactionRequest.agent_id == agent_id)
            
        return query.order_by(models.TransactionRequest.created_at.desc()).all()

    @staticmethod
    def get_by_id(db: Session, inquiry_id: int) -> Optional[models.TransactionRequest]:
        return db.query(models.TransactionRequest).filter(models.TransactionRequest.id == inquiry_id).first()

    @staticmethod
    def commit(db: Session):
        db.commit()

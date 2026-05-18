from sqlalchemy.orm import Session
from typing import List, Optional, Any
import models

class UserRepository:
    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.email == email).first()

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.id == user_id).first()

    @staticmethod
    def get_agent_by_id(db: Session, agent_id: int) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.id == agent_id, models.User.role == "agent").first()

    @staticmethod
    def create(db: Session, user_obj: models.User) -> models.User:
        db.add(user_obj)
        db.commit()
        db.refresh(user_obj)
        return user_obj

    @staticmethod
    def get_team_staff(db: Session, manager_id: int) -> List[models.User]:
        return db.query(models.User).filter(models.User.manager_id == manager_id, models.User.role == "agent").all()

    @staticmethod
    def get_all_agents(db: Session) -> List[models.User]:
        return db.query(models.User).filter(models.User.role == "agent").all()

    @staticmethod
    def get_all_staff(db: Session) -> List[models.User]:
        return db.query(models.User).filter(models.User.role != "client").all()

    @staticmethod
    def get_head_agents(db: Session) -> List[models.User]:
        return db.query(models.User).filter(models.User.role == "head_agent").all()

    @staticmethod
    def commit(db: Session):
        db.commit()

    @staticmethod
    def refresh(db: Session, obj: Any):
        db.refresh(obj)

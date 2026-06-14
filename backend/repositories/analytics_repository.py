from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional, Any
import models

class AnalyticsRepository:
    @staticmethod
    def get_property_status_counts(db: Session, agent_ids: Optional[list[int]] = None) -> dict:
        query = db.query(models.Property.status, func.count(models.Property.id))
        if agent_ids is not None:
            query = query.filter(models.Property.agent_id.in_(agent_ids))
        status_counts = query.group_by(models.Property.status).all()
        return {row[0]: row[1] for row in status_counts}

    @staticmethod
    def get_total_sales_value(db: Session, status: str = 'sold') -> float:
        return db.query(func.sum(models.Property.price)).filter(models.Property.status == status).scalar() or 0

    @staticmethod
    def get_top_agents(db: Session, limit: int = 5) -> list:
        return db.query(
            models.User.full_name,
            func.count(models.Property.id).label('sold_count')
        ).join(models.Property, models.User.id == models.Property.agent_id)\
        .filter(models.Property.status == 'sold')\
        .group_by(models.User.id)\
        .order_by(func.count(models.Property.id).desc())\
        .limit(limit).all()

    @staticmethod
    def get_role_counts(db: Session) -> dict:
        role_counts = db.query(models.User.role, func.count(models.User.id)).group_by(models.User.role).all()
        return {row[0]: row[1] for row in role_counts}

    @staticmethod
    def get_transaction_request_pipeline_counts(db: Session) -> dict:
        pipeline_counts = db.query(
            models.TransactionRequest.status,
            func.count(models.TransactionRequest.id)
        ).group_by(models.TransactionRequest.status).all()
        return {row[0]: row[1] for row in pipeline_counts}


    @staticmethod
    def get_team_performance(db: Session, team_ids: list[int]) -> list:
        return db.query(
            models.User.full_name,
            func.count(models.Property.id).label('closed_deals')
        ).join(models.Property, models.User.id == models.Property.agent_id)\
        .filter(models.Property.agent_id.in_(team_ids))\
        .filter(models.Property.status.in_(['sold', 'rented']))\
        .group_by(models.User.id).all()

    @staticmethod
    def get_visit_status_counts(db: Session, agent_id: int) -> dict:
        visit_counts = db.query(models.Visit.status, func.count(models.Visit.id))\
            .filter(models.Visit.agent_id == agent_id)\
            .group_by(models.Visit.status).all()
        return {row[0]: row[1] for row in visit_counts}

    @staticmethod
    def get_visits_history(db: Session, agent_id: int, since: datetime) -> list:
        return db.query(models.Visit.visit_date)\
            .filter(models.Visit.agent_id == agent_id)\
            .filter(models.Visit.visit_date >= since).all()

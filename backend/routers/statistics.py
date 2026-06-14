from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, database, auth
from datetime import datetime, timedelta
from repositories.analytics_repository import AnalyticsRepository

router = APIRouter(
    prefix="/statistics",
    tags=["Statistics & Analytics"]
)

@router.get("/admin")
def get_admin_statistics(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    auth.RoleChecker(["admin"])(current_user)
    
    # 1. Properties by Status
    property_statuses = AnalyticsRepository.get_property_status_counts(db)
    
    # 2. Total properties value
    total_sales_value = AnalyticsRepository.get_total_sales_value(db, 'sold')
    total_rent_value = AnalyticsRepository.get_total_sales_value(db, 'rented')

    # 3. Top Agents by Sold Properties
    top_agents = AnalyticsRepository.get_top_agents(db)
    top_agents_data = [{"agent": row[0], "sold": row[1]} for row in top_agents]
    
    # 4. User Roles Breakdown
    user_roles = AnalyticsRepository.get_role_counts(db)

    # 5. Transaction Request Pipeline
    transaction_requests_pipeline = AnalyticsRepository.get_transaction_request_pipeline_counts(db)
    
    return {
        "property_statuses": property_statuses,
        "revenue": {
            "sales": float(total_sales_value),
            "rentals": float(total_rent_value)
        },
        "top_agents": top_agents_data,
        "user_roles": user_roles,
        "transaction_requests_pipeline": transaction_requests_pipeline
    }


@router.get("/agency")
def get_agency_statistics(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    auth.RoleChecker(["head_agent", "admin"])(current_user)
    
    # Get all agents managed by this head_agent (or all if admin checks this)
    team_agents = db.query(models.User).filter(models.User.manager_id == current_user.id).all()
    team_ids = [a.id for a in team_agents] + [current_user.id]

    # 1. Team's properties by status
    property_statuses = AnalyticsRepository.get_property_status_counts(db, agent_ids=team_ids)

    # 2. Team Member Performance (Sold/Rented properties)
    performance = AnalyticsRepository.get_team_performance(db, team_ids)
    team_performance = [{"agent": row[0], "deals": row[1]} for row in performance]
    
    # Fill in agents with 0 deals
    agent_names_with_deals = [p["agent"] for p in team_performance]
    for agent in team_agents:
        if agent.full_name not in agent_names_with_deals:
            team_performance.append({"agent": agent.full_name, "deals": 0})
            
    return {
        "property_statuses": property_statuses,
        "team_performance": team_performance,
        "total_team_members": len(team_agents)
    }

@router.get("/agent")
def get_agent_statistics(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    # Standard agent or head_agent
    
    # 1. My properties by status
    property_statuses = AnalyticsRepository.get_property_status_counts(db, agent_ids=[current_user.id])
    
    # 2. Visit conversions / statuses
    visit_statuses = AnalyticsRepository.get_visit_status_counts(db, current_user.id)
    
    # 3. Monthly Activity (last 6 months)
    six_months_ago = datetime.now() - timedelta(days=180)
    visits_history = AnalyticsRepository.get_visits_history(db, current_user.id, six_months_ago)
        
    monthly_counts = {}
    for (v_date,) in visits_history:
        month_key = v_date.strftime("%b %Y")
        monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1

    return {
        "property_statuses": property_statuses,
        "visit_statuses": visit_statuses,
        "monthly_visits": monthly_counts
    }

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
import models, database, auth
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/statistics",
    tags=["Statistics & Analytics"]
)

@router.get("/admin")
def get_admin_statistics(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    auth.RoleChecker(["admin"])(current_user)
    
    # 1. Properties by Status
    status_counts = db.query(models.Property.status, func.count(models.Property.id)).group_by(models.Property.status).all()
    property_statuses = {row[0]: row[1] for row in status_counts}
    
    # 2. Total properties value (Assuming only "sold" price matters)
    total_sales_value = db.query(func.sum(models.Property.price)).filter(models.Property.status == 'sold').scalar() or 0
    total_rent_value = db.query(func.sum(models.Property.price)).filter(models.Property.status == 'rented').scalar() or 0

    # 3. Top Agents by Sold Properties
    top_agents = db.query(
        models.User.full_name,
        func.count(models.Property.id).label('sold_count')
    ).join(models.Property, models.User.id == models.Property.agent_id)\
    .filter(models.Property.status == 'sold')\
    .group_by(models.User.id)\
    .order_by(func.count(models.Property.id).desc())\
    .limit(5).all()
    
    top_agents_data = [{"agent": row[0], "sold": row[1]} for row in top_agents]
    
    # 4. User Roles Breakdown
    role_counts = db.query(models.User.role, func.count(models.User.id)).group_by(models.User.role).all()
    user_roles = {row[0]: row[1] for row in role_counts}
    
    return {
        "property_statuses": property_statuses,
        "revenue": {
            "sales": float(total_sales_value),
            "rentals": float(total_rent_value)
        },
        "top_agents": top_agents_data,
        "user_roles": user_roles
    }

@router.get("/agency")
def get_agency_statistics(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    auth.RoleChecker(["head_agent", "admin"])(current_user)
    
    # Get all agents managed by this head_agent (or all if admin checks this)
    team_agents = db.query(models.User).filter(models.User.manager_id == current_user.id).all()
    team_ids = [a.id for a in team_agents] + [current_user.id]

    # 1. Team's properties by status
    status_counts = db.query(models.Property.status, func.count(models.Property.id))\
        .filter(models.Property.agent_id.in_(team_ids))\
        .group_by(models.Property.status).all()
    property_statuses = {row[0]: row[1] for row in status_counts}

    # 2. Team Member Performance (Sold/Rented properties)
    performance = db.query(
        models.User.full_name,
        func.count(models.Property.id).label('closed_deals')
    ).join(models.Property, models.User.id == models.Property.agent_id)\
    .filter(models.Property.agent_id.in_(team_ids))\
    .filter(models.Property.status.in_(['sold', 'rented']))\
    .group_by(models.User.id).all()
    
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
    status_counts = db.query(models.Property.status, func.count(models.Property.id))\
        .filter(models.Property.agent_id == current_user.id)\
        .group_by(models.Property.status).all()
    property_statuses = {row[0]: row[1] for row in status_counts}
    
    # 2. Visit conversions / statuses
    visit_counts = db.query(models.Visit.status, func.count(models.Visit.id))\
        .filter(models.Visit.agent_id == current_user.id)\
        .group_by(models.Visit.status).all()
    visit_statuses = {row[0]: row[1] for row in visit_counts}
    
    # 3. Monthly Activity (last 6 months created_at visits)
    six_months_ago = datetime.now() - timedelta(days=180)
    monthly_visits = db.query(
        func.date_trunc('month', models.Visit.visit_date).label('month'),
        func.count(models.Visit.id)
    ).filter(models.Visit.agent_id == current_user.id)\
     .filter(models.Visit.visit_date >= six_months_ago)\
     .group_by(func.date_trunc('month', models.Visit.visit_date))\
     .order_by('month').all()
     
    # SQLite uses string for dates, postgres uses date_trunc. The easiest safe way is group_by month.
    # To be fully safe across sqlite/postgres, we handle formatting in Python
    visits_history = db.query(models.Visit.visit_date)\
        .filter(models.Visit.agent_id == current_user.id)\
        .filter(models.Visit.visit_date >= six_months_ago).all()
        
    monthly_counts = {}
    for (v_date,) in visits_history:
        month_key = v_date.strftime("%b %Y")
        monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1

    return {
        "property_statuses": property_statuses,
        "visit_statuses": visit_statuses,
        "monthly_visits": monthly_counts
    }

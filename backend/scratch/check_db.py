from sqlalchemy.orm import Session
from database import SessionLocal
import models

def check_agent_properties():
    db = SessionLocal()
    try:
        agent = db.query(models.User).filter(models.User.email == "killer.chebbi@gmail.com").first()
        if not agent:
            print("Agent not found")
            return
        
        print(f"Agent: {agent.full_name} (ID: {agent.id}, Role: {agent.role})")
        
        properties = db.query(models.Property).filter(models.Property.agent_id == agent.id).all()
        print(f"Found {len(properties)} properties assigned to this agent.")
        for p in properties:
            print(f" - {p.title} (ID: {p.id})")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_agent_properties()

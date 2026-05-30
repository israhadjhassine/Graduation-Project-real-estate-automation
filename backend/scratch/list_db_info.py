import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
import models

def inspect():
    db = SessionLocal()
    try:
        users = db.query(models.User).all()
        print("--- USERS IN DB ---")
        for u in users:
            print(f"ID: {u.id} | Email: {u.email} | Role: {u.role} | Name: {u.full_name}")

        properties = db.query(models.Property).all()
        print("\n--- PROPERTIES IN DB ---")
        for p in properties:
            print(f"ID: {p.id} | Title: {p.title} | Agent ID: {p.agent_id} | Owner ID: {p.owner_id}")
            
    finally:
        db.close()

if __name__ == "__main__":
    inspect()

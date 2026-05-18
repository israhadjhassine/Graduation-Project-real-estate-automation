import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to sys.path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models

DATABASE_URL = "postgresql://postgres:admin@localhost:5432/real_estate"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def list_users():
    db = SessionLocal()
    try:
        users = db.query(models.User).all()
        print("ID | Email | Name | Role")
        print("-" * 50)
        for u in users:
            print(f"{u.id} | {u.email} | {u.full_name} | {u.role}")
    except Exception as e:
        print("Error connecting/querying database:", e)
    finally:
        db.close()

if __name__ == "__main__":
    list_users()

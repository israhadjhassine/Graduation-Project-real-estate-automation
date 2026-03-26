import sys
import os
from sqlalchemy.orm import Session
from database import SessionLocal
import models

def check_data():
    db = SessionLocal()
    try:
        print("--- Properties ---")
        properties = db.query(models.Property).all()
        for p in properties:
            print(f"ID: {p.id}, Title: {p.title}, Slug: {p.slug}, Status: {p.status}")
            print(f"  Images Count: {len(p.images)}")
            for img in p.images:
                print(f"    - Image ID: {img.id}, URL: {img.image_url}")
            
        print("\n--- All Images in DB ---")
        images = db.query(models.PropertyImage).all()
        for img in images:
            print(f"ID: {img.id}, PropID: {img.property_id}, URL: {img.image_url}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_data()

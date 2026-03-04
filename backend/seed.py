import sys
import os

# Add the current directory to sys.path so we can import from the same folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import auth
import ai_utils
from datetime import datetime

def seed_db():
    print("🚀 Starting Database Seeding...")
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Clear existing data
        db.query(models.Visit).delete()
        db.query(models.Inquiry).delete()
        db.query(models.PropertyImage).delete()
        db.query(models.PropertyFavorite).delete()
        db.query(models.Feature).delete()
        db.query(models.Property).delete()
        db.query(models.User).delete()
        db.commit()

        # 2. Create Users
        print("👥 Creating Users...")
        admin = models.User(email="admin@elite.tn", full_name="Sami Ben Ali", role="admin", hashed_password=auth.get_password_hash("adminpassword"))
        db.add(admin)
        user_isra1 = models.User(email="israhadjhassine@gmail.com", full_name="Isra Hadj Hassine", role="admin", hashed_password=auth.get_password_hash("123"))
        db.add(user_isra1)
        user_isra2 = models.User(email="isra@gmail.com", full_name="Isra", role="admin", hashed_password=auth.get_password_hash("123"))
        db.add(user_isra2)
        manager = models.User(email="manager@elite.tn", full_name="Laila Mansour", role="head_agent", hashed_password=auth.get_password_hash("managerpassword"))
        db.add(manager)
        db.commit()
        db.refresh(manager)

        agent1 = models.User(email="agent1@elite.tn", full_name="Ahmed Trabelsi", role="agent", hashed_password=auth.get_password_hash("agentpassword"), manager_id=manager.id)
        db.add(agent1)
        agent2 = models.User(email="agent2@elite.tn", full_name="Amira Ghorbel", role="agent", hashed_password=auth.get_password_hash("agentpassword"), manager_id=manager.id)
        db.add(agent2)
        visitor = models.User(email="visitor@test.com", full_name="John Doe", role="visitor", hashed_password=auth.get_password_hash("visitorpassword"))
        db.add(visitor)
        db.commit()

        created_users = {
            "manager@elite.tn": manager,
            "agent1@elite.tn": agent1,
            "agent2@elite.tn": agent2
        }

        # 4. Create Features
        print("✨ Creating Features...")
        features_list = ["Swimming Pool", "Garden", "Sea View", "Smart Home", "Gym", "Garage", "High-speed Internet"]
        created_features = {}
        for f_name in features_list:
            feature = models.Feature(name=f_name)
            db.add(feature)
            created_features[f_name] = feature
        
        db.commit()

        # 5. Create Properties
        print("🏠 Creating Properties...")
        properties_data = [
            {
                "title": "Modern Azure Villa",
                "slug": "modern-azure-villa",
                "description": "A stunning modern villa with panoramic sea views and a private infinity pool. Perfect for luxury seekers.",
                "price": 1250000,
                "type": "villa",
                "listing": "sale",
                "city": "Hammamet",
                "country": "Tunisia",
                "bedrooms": 5,
                "bathrooms": 4,
                "area": 450,
                "image": "/static/seed-images/villa.png",
                "agent": "agent1@elite.tn",
                "features": ["Swimming Pool", "Sea View", "Smart Home", "Garage"]
            },
            {
                "title": "Skyline Luxury Apartment",
                "slug": "skyline-luxury-apartment",
                "description": "Premium 20th-floor apartment in the heart of Tunis. Features floor-to-ceiling windows and world-class finishings.",
                "price": 4500,
                "type": "apartment",
                "listing": "rent",
                "city": "Tunis",
                "country": "Tunisia",
                "bedrooms": 3,
                "bathrooms": 2,
                "area": 180,
                "image": "/static/seed-images/apartment.png",
                "agent": "agent2@elite.tn",
                "features": ["Gym", "High-speed Internet", "Garage"]
            },
            {
                "title": "Garden Heritage House",
                "slug": "garden-heritage-house",
                "description": "Charming traditional house with a massive private garden. Ideal for peaceful family living.",
                "price": 850000,
                "type": "house",
                "listing": "sale",
                "city": "Marsa",
                "country": "Tunisia",
                "bedrooms": 4,
                "bathrooms": 3,
                "area": 320,
                "image": "/static/seed-images/house.png",
                "agent": "agent1@elite.tn",
                "features": ["Garden", "Garage"]
            }
        ]

        for p in properties_data:
            prop = models.Property(
                title=p["title"],
                slug=p["slug"],
                description=p["description"],
                price=p["price"],
                property_type=p["type"],
                listing_type=p["listing"],
                city=p["city"],
                country=p["country"],
                bedrooms=p["bedrooms"],
                bathrooms=p["bathrooms"],
                area=p["area"],
                agent_id=created_users[p["agent"]].id,
                owner_id=created_users["manager@elite.tn"].id,
                published_at=datetime.utcnow()
            )
            
            # Add features
            for f_name in p["features"]:
                prop.features.append(created_features[f_name])
            
            db.add(prop)
            db.commit() # Commit to get property ID
            
            # Add images
            img = models.PropertyImage(
                property_id=prop.id,
                image_url=p["image"],
                is_primary=True
            )
            db.add(img)
            
        db.commit()
        print("✅ Seeding Completed Successfully!")

    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()

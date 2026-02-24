import sys
import os

# Add the current directory to sys.path so we can import from the same folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import auth
from datetime import datetime

def seed_db():
    print("🚀 Starting Database Seeding...")
    db = SessionLocal()
    
    try:
        # 1. Clear existing data (Optional, be careful with this in production!)
        # db.query(models.PropertyImage).delete()
        # db.query(models.Property).delete()
        # db.query(models.User).delete()
        # db.query(models.Agency).delete()
        # db.commit()

        # 2. Create an Agency
        print("🏢 Creating Agency...")
        agency = models.Agency(
            name="Elite Real Estate Tunisia",
            license_number="LIC-2026-001"
        )
        db.add(agency)
        db.commit()
        db.refresh(agency)

        # 3. Create Users
        print("👥 Creating Users...")
        users_data = [
            {"email": "admin@elite.tn", "full_name": "Sami Ben Ali", "role": "admin", "password": "adminpassword"},
            {"email": "manager@elite.tn", "full_name": "Laila Mansour", "role": "head_agent", "password": "managerpassword"},
            {"email": "agent1@elite.tn", "full_name": "Ahmed Trabelsi", "role": "agent", "password": "agentpassword"},
            {"email": "agent2@elite.tn", "full_name": "Amira Ghorbel", "role": "agent", "password": "agentpassword"},
            {"email": "visitor@test.com", "full_name": "John Doe", "role": "visitor", "password": "visitorpassword"},
        ]

        created_users = {}
        for u in users_data:
            hashed_pwd = auth.get_password_hash(u["password"])
            user = models.User(
                email=u["email"],
                full_name=u["full_name"],
                hashed_password=hashed_pwd,
                role=u["role"],
                agency_id=agency.id if u["role"] != "visitor" else None
            )
            db.add(user)
            created_users[u["email"]] = user
        
        db.commit()

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
                "image": "/seed-images/villa.png",
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
                "image": "/seed-images/apartment.png",
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
                "image": "/seed-images/house.png",
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
                agency_id=agency.id,
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

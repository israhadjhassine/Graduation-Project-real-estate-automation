import sys
import os

# Add the current directory to sys.path so we can import from the same folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import auth
import ai_utils
from utils import embeddings
from datetime import datetime

def seed_db():
    print("🚀 Starting Database Seeding...")
    # models.Base.metadata.drop_all(bind=engine)
    # models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Clear existing data
        db.query(models.Visit).delete()
        db.query(models.PropertyImage).delete()
        db.query(models.PropertyFavorite).delete()
        db.query(models.Feature).delete()
        db.query(models.Property).delete()
        db.query(models.User).delete()
        db.commit()

        # 2. Create Users
        print("👥 Creating Users...")
        # Admins
        admin1 = models.User(email="admin@elite.tn", full_name="Sami Ben Ali", role="admin", hashed_password=auth.get_password_hash("adminpassword"))
        db.add(admin1)
        user_isra = models.User(email="israhadjhassine@gmail.com", full_name="Isra Hadj Hassine", role="admin", hashed_password=auth.get_password_hash("123"))
        db.add(user_isra)
        
        # Head Agents (Managers)
        head1 = models.User(email="h.kallel@elite.tn", full_name="Hedi Kallel", role="head_agent", hashed_password=auth.get_password_hash("managerpassword"))
        db.add(head1)
        
        db.commit()
        db.refresh(head1)

        # Sub-Agents (All managed by Hedi Kallel)
        agent1 = models.User(email="a.trabelsi@elite.tn", full_name="Ahmed Trabelsi", role="agent", hashed_password=auth.get_password_hash("agentpassword"), manager_id=head1.id)
        agent2 = models.User(email="s.dridi@elite.tn", full_name="Sonia Dridi", role="agent", hashed_password=auth.get_password_hash("agentpassword"), manager_id=head1.id)
        agent3 = models.User(email="k.jelassi@elite.tn", full_name="Karim Jelassi", role="agent", hashed_password=auth.get_password_hash("agentpassword"), manager_id=head1.id)
        agent4 = models.User(email="n.moussa@elite.tn", full_name="Nadine Moussa", role="agent", hashed_password=auth.get_password_hash("agentpassword"), manager_id=head1.id)
        
        db.add_all([agent1, agent2, agent3, agent4])
        
        # Visitor
        visitor = models.User(email="visitor@test.com", full_name="John Doe", role="visitor", hashed_password=auth.get_password_hash("visitorpassword"))
        db.add(visitor)
        
        db.commit()

        # 4. Create Features
        print("✨ Creating Features...")
        features_list = ["Swimming Pool", "Garden", "Sea View", "Smart Home", "Gym", "Garage", "High-speed Internet", "Central Heating", "Elevator"]
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
                "title": "Ocean Breeze Mansion",
                "slug": "ocean-breeze-mansion",
                "description": "Luxurious 6-bedroom mansion in Gammarth with direct beach access and infinity pool.",
                "price": 3500000,
                "type": "villa",
                "listing": "sale",
                "city": "Gammarth",
                "country": "Tunisia",
                "bedrooms": 6,
                "bathrooms": 5,
                "area": 850,
                "image": "/static/seed-images/villa.png",
                "agent_email": "a.trabelsi@elite.tn",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Swimming Pool", "Sea View", "Smart Home", "Garage", "Garden"],
                "latitude": 36.9156,
                "longitude": 10.2915
            },
            {
                "title": "Blue Horizon Penthouse",
                "slug": "blue-horizon-penthouse",
                "description": "Contemporary penthouse overlooking the Gulf of Tunis. High-end finishings and spacious terrace.",
                "price": 5500,
                "type": "apartment",
                "listing": "rent",
                "city": "Sidi Bou Said",
                "country": "Tunisia",
                "bedrooms": 3,
                "bathrooms": 2,
                "area": 220,
                "image": "/static/seed-images/apartment.png",
                "agent_email": "s.dridi@elite.tn",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Sea View", "Elevator", "Gym", "Garage"],
                "latitude": 36.8706,
                "longitude": 10.3417
            },
            {
                "title": "Mediterranean Dream Estate",
                "slug": "mediterranean-dream-estate",
                "description": "Exclusive estate in Hammamet North. Features olive groves and private tennis court.",
                "price": 2800000,
                "type": "villa",
                "listing": "sale",
                "city": "Hammamet",
                "country": "Tunisia",
                "bedrooms": 5,
                "bathrooms": 4,
                "area": 1200,
                "image": "/static/seed-images/house.png",
                "agent_email": "k.jelassi@elite.tn",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Swimming Pool", "Garden", "Garage"],
                "latitude": 36.4000,
                "longitude": 10.6167
            },
            {
                "title": "Urban Oasis Lofts",
                "slug": "urban-oasis-lofts",
                "description": "Chic industrial loft in Lac 2. Perfect for young professionals near the business district.",
                "price": 2200,
                "type": "apartment",
                "listing": "rent",
                "city": "Lac 2",
                "country": "Tunisia",
                "bedrooms": 2,
                "bathrooms": 1,
                "area": 110,
                "image": "/static/seed-images/apartment.png",
                "agent_email": "n.moussa@elite.tn",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Smart Home", "Gym", "High-speed Internet"],
                "latitude": 36.8359,
                "longitude": 10.2367
            }
        ]

        # Map emails to IDs for quick lookup
        user_map = {u.email: u.id for u in db.query(models.User).all()}

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
                agent_id=user_map[p["agent_email"]],
                owner_id=user_map[p["owner_email"]],
                published_at=datetime.utcnow(),
                latitude=p.get("latitude"),
                longitude=p.get("longitude"),
                description_vector=embeddings.get_embedding(p["description"])
            )
            
            for f_name in p["features"]:
                prop.features.append(created_features[f_name])
            
            db.add(prop)
            db.commit()
            
            img = models.PropertyImage(property_id=prop.id, image_url=p["image"], is_primary=True)
            db.add(img)

        # 6. Create Sample Interactions
        print("💬 Creating Interactions...")
        
        db.commit()
        print("✅ Seeding Completed Successfully!")

    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()

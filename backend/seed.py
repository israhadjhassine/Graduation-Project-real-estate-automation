import sys
import os

# Add the current directory to sys.path so we can import from the same folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
import auth
from services import ai
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
        db.query(models.Feature).delete()
        db.query(models.Property).delete()
        db.query(models.User).delete()
        db.commit()

        # 2. Create Users
        print("👥 Creating Users...")
        # Admins
        user_isra = models.User(email="israhadjhassine@gmail.com", full_name="Isra Hadj Hassine", role="admin", hashed_password=auth.get_password_hash("123"))
        db.add(user_isra)
        
        # Head Agents (Managers)
        head1 = models.User(email="h.kallel@elite.tn", full_name="Hedi Kallel", role="head_agent", hashed_password=auth.get_password_hash("managerpassword"))
        db.add(head1)
        
        db.commit()
        db.refresh(head1)

        # Sub-Agents (All managed by Hedi Kallel)
        agent1 = models.User(
            email="killer.chebbi@gmail.com", 
            full_name="Ahmed Trabelsi", 
            role="agent", 
            google_calendar_id="68f19bf32d864818eaae2b335012dab02672fa7b902b340c81aaad5c6f9bc632@group.calendar.google.com",
            hashed_password=auth.get_password_hash("agentpassword"), 
            manager_id=head1.id
        )
        agent2 = models.User(email="s.dridi@elite.tn", full_name="Sonia Dridi", role="agent", hashed_password=auth.get_password_hash("agentpassword"), manager_id=head1.id)
        agent3 = models.User(email="k.jelassi@elite.tn", full_name="Karim Jelassi", role="agent", hashed_password=auth.get_password_hash("agentpassword"), manager_id=head1.id)
        agent4 = models.User(email="n.moussa@elite.tn", full_name="Nadine Moussa", role="agent", hashed_password=auth.get_password_hash("agentpassword"), manager_id=head1.id)
        
        db.add_all([agent1, agent2, agent3, agent4])
        
        # Client (for testing visits)
        client = models.User(email="client@test.com", full_name="John Client", role="client", hashed_password=auth.get_password_hash("clientpassword"))
        db.add(client)
        
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
                "agent_email": "killer.chebbi@gmail.com",
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
            },
            {
                "title": "Golden Sands Villa",
                "slug": "golden-sands-villa",
                "description": "Stunning beachfront villa in Hammamet with a private pool and large garden.",
                "price": 1200000,
                "type": "villa",
                "listing": "sale",
                "city": "Hammamet",
                "country": "Tunisia",
                "bedrooms": 4,
                "bathrooms": 3,
                "area": 450,
                "image": "/static/seed-images/villa.png",
                "agent_email": "killer.chebbi@gmail.com",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Swimming Pool", "Garden", "Garage"],
                "latitude": 36.4,
                "longitude": 10.6
            },
            {
                "title": "Carthage Heritage House",
                "slug": "carthage-heritage-house",
                "description": "Historical mansion in the heart of Carthage, combining traditional architecture with modern comfort.",
                "price": 4500000,
                "type": "villa",
                "listing": "sale",
                "city": "Carthage",
                "country": "Tunisia",
                "bedrooms": 7,
                "bathrooms": 6,
                "area": 950,
                "image": "/static/seed-images/house.png",
                "agent_email": "s.dridi@elite.tn",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Garden", "Garage", "Central Heating"],
                "latitude": 36.85,
                "longitude": 10.32
            },
            {
                "title": "Emerald Garden Apartment",
                "slug": "emerald-garden-apartment",
                "description": "Bright and airy apartment in La Marsa with a beautiful view of the central park.",
                "price": 3500,
                "type": "apartment",
                "listing": "rent",
                "city": "La Marsa",
                "country": "Tunisia",
                "bedrooms": 3,
                "bathrooms": 2,
                "area": 180,
                "image": "/static/seed-images/apartment.png",
                "agent_email": "k.jelassi@elite.tn",
                "owner_email": "h.kallel@elite.tn",
                "features": ["High-speed Internet", "Elevator", "Garage"],
                "latitude": 36.88,
                "longitude": 10.33
            },
            {
                "title": "Sapphire Bay Residence",
                "slug": "sapphire-bay-residence",
                "description": "Modern apartment located right on the Bizerte Corniche, offering breathtaking sea views.",
                "price": 2800,
                "type": "apartment",
                "listing": "rent",
                "city": "Bizerte",
                "country": "Tunisia",
                "bedrooms": 2,
                "bathrooms": 2,
                "area": 140,
                "image": "/static/seed-images/apartment.png",
                "agent_email": "n.moussa@elite.tn",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Sea View", "Smart Home", "Elevator"],
                "latitude": 37.27,
                "longitude": 9.87
            },
            {
                "title": "Olive Grove Retreat",
                "slug": "olive-grove-retreat",
                "description": "Peaceful villa surrounded by olive trees in Nabeul, perfect for a quiet family life.",
                "price": 850000,
                "type": "villa",
                "listing": "sale",
                "city": "Nabeul",
                "country": "Tunisia",
                "bedrooms": 3,
                "bathrooms": 2,
                "area": 320,
                "image": "/static/seed-images/villa.png",
                "agent_email": "killer.chebbi@gmail.com",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Garden", "Garage", "Central Heating"],
                "latitude": 36.45,
                "longitude": 10.73
            },
            {
                "title": "Skyline Business Suite",
                "slug": "skyline-business-suite",
                "description": "High-end suite in the Berges du Lac business district, ideal for corporate executives.",
                "price": 4200,
                "type": "apartment",
                "listing": "rent",
                "city": "Tunis",
                "country": "Tunisia",
                "bedrooms": 2,
                "bathrooms": 2,
                "area": 160,
                "image": "/static/seed-images/apartment.png",
                "agent_email": "s.dridi@elite.tn",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Smart Home", "Gym", "Garage", "Elevator"],
                "latitude": 36.84,
                "longitude": 10.2
            },
            {
                "title": "Jasmine Valley Estate",
                "slug": "jasmine-valley-estate",
                "description": "Upscale villa in Ennasr with a panoramic view of the city of Tunis.",
                "price": 950000,
                "type": "villa",
                "listing": "sale",
                "city": "Ennasr",
                "country": "Tunisia",
                "bedrooms": 4,
                "bathrooms": 3,
                "area": 380,
                "image": "/static/seed-images/house.png",
                "agent_email": "k.jelassi@elite.tn",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Garage", "Garden", "Central Heating"],
                "latitude": 36.86,
                "longitude": 10.16
            },
            {
                "title": "Coral Reef Cottage",
                "slug": "coral-reef-cottage",
                "description": "Cozy cottage near the forests and beaches of Tabarka, great for vacation rentals.",
                "price": 1500,
                "type": "house",
                "listing": "rent",
                "city": "Tabarka",
                "country": "Tunisia",
                "bedrooms": 2,
                "bathrooms": 1,
                "area": 90,
                "image": "/static/seed-images/house.png",
                "agent_email": "n.moussa@elite.tn",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Garden", "Sea View"],
                "latitude": 36.95,
                "longitude": 8.75
            },
            {
                "title": "Ancient City Loft",
                "slug": "ancient-city-loft",
                "description": "Authentic loft in the heart of the Kairouan Medina, beautifully restored.",
                "price": 450000,
                "type": "apartment",
                "listing": "sale",
                "city": "Kairouan",
                "country": "Tunisia",
                "bedrooms": 1,
                "bathrooms": 1,
                "area": 75,
                "image": "/static/seed-images/apartment.png",
                "agent_email": "killer.chebbi@gmail.com",
                "owner_email": "h.kallel@elite.tn",
                "features": ["High-speed Internet"],
                "latitude": 35.67,
                "longitude": 10.1
            },
            {
                "title": "Desert Rose Villa",
                "slug": "desert-rose-villa",
                "description": "Luxury villa in Tozeur with traditional brickwork and a private oasis garden.",
                "price": 3200,
                "type": "villa",
                "listing": "rent",
                "city": "Tozeur",
                "country": "Tunisia",
                "bedrooms": 3,
                "bathrooms": 3,
                "area": 280,
                "image": "/static/seed-images/villa.png",
                "agent_email": "s.dridi@elite.tn",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Swimming Pool", "Garden", "Garage"],
                "latitude": 33.92,
                "longitude": 8.13
            },
            {
                "title": "Azure Coast Villa",
                "slug": "azure-coast-villa",
                "description": "Exquisite villa in Kelibia with a panoramic view of the Mediterranean and the historic fort.",
                "price": 1850000,
                "type": "villa",
                "listing": "sale",
                "city": "Kelibia",
                "country": "Tunisia",
                "bedrooms": 5,
                "bathrooms": 4,
                "area": 520,
                "image": "/static/seed-images/villa.png",
                "agent_email": "k.jelassi@elite.tn",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Sea View", "Swimming Pool", "Garden"],
                "latitude": 36.85,
                "longitude": 11.1
            },
            {
                "title": "Palm Grove Apartment",
                "slug": "palm-grove-apartment",
                "description": "Traditional Djerbian style apartment within a palm grove, offering peace and serenity.",
                "price": 2200,
                "type": "apartment",
                "listing": "rent",
                "city": "Djerba",
                "country": "Tunisia",
                "bedrooms": 2,
                "bathrooms": 1,
                "area": 120,
                "image": "/static/seed-images/apartment.png",
                "agent_email": "n.moussa@elite.tn",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Garden", "High-speed Internet"],
                "latitude": 33.87,
                "longitude": 10.85
            },
            {
                "title": "Roman Ruins View Apartment",
                "slug": "roman-ruins-view",
                "description": "Unique apartment in El Jem with a direct view of the world-famous Roman amphitheater.",
                "price": 320000,
                "type": "apartment",
                "listing": "sale",
                "city": "El Jem",
                "country": "Tunisia",
                "bedrooms": 2,
                "bathrooms": 1,
                "area": 105,
                "image": "/static/seed-images/apartment.png",
                "agent_email": "killer.chebbi@gmail.com",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Elevator", "Garage"],
                "latitude": 35.3,
                "longitude": 10.7
            },
            {
                "title": "Mountain Peak Lodge",
                "slug": "mountain-peak-lodge",
                "description": "Rustic wooden lodge in the mountains of Ain Draham, perfect for winter getaways.",
                "price": 1800,
                "type": "house",
                "listing": "rent",
                "city": "Ain Draham",
                "country": "Tunisia",
                "bedrooms": 3,
                "bathrooms": 2,
                "area": 150,
                "image": "/static/seed-images/house.png",
                "agent_email": "s.dridi@elite.tn",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Central Heating", "Garden"],
                "latitude": 36.78,
                "longitude": 8.68
            },
            {
                "title": "Sun-Kissed Bungalow",
                "slug": "sun-kissed-bungalow",
                "description": "Charming bungalow in Mahdia, just steps away from the crystal clear turquoise waters.",
                "price": 650000,
                "type": "house",
                "listing": "sale",
                "city": "Mahdia",
                "country": "Tunisia",
                "bedrooms": 3,
                "bathrooms": 2,
                "area": 210,
                "image": "/static/seed-images/house.png",
                "agent_email": "k.jelassi@elite.tn",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Sea View", "Garden"],
                "latitude": 35.5,
                "longitude": 11.06
            },
            {
                "title": "Lavender Fields Estate",
                "slug": "lavender-fields-estate",
                "description": "Large countryside estate in Tebourba with vast lands and a modern farmhouse.",
                "price": 1100000,
                "type": "villa",
                "listing": "sale",
                "city": "Tebourba",
                "country": "Tunisia",
                "bedrooms": 4,
                "bathrooms": 3,
                "area": 400,
                "image": "/static/seed-images/villa.png",
                "agent_email": "n.moussa@elite.tn",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Garden", "Garage", "Smart Home"],
                "latitude": 36.83,
                "longitude": 9.84
            },
            {
                "title": "Old Port Studio",
                "slug": "old-port-studio",
                "description": "Compact and stylish studio in the historic Old Port area of Bizerte.",
                "price": 1200,
                "type": "apartment",
                "listing": "rent",
                "city": "Bizerte",
                "country": "Tunisia",
                "bedrooms": 1,
                "bathrooms": 1,
                "area": 55,
                "image": "/static/seed-images/apartment.png",
                "agent_email": "killer.chebbi@gmail.com",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Sea View", "High-speed Internet"],
                "latitude": 37.28,
                "longitude": 9.88
            },
            {
                "title": "Central Park Residence",
                "slug": "central-park-residence",
                "description": "Modern apartment in a quiet residential area of Ariana, close to all amenities.",
                "price": 2400,
                "type": "apartment",
                "listing": "rent",
                "city": "Ariana",
                "country": "Tunisia",
                "bedrooms": 3,
                "bathrooms": 2,
                "area": 165,
                "image": "/static/seed-images/apartment.png",
                "agent_email": "s.dridi@elite.tn",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Elevator", "Garage", "Smart Home"],
                "latitude": 36.86,
                "longitude": 10.19
            },
            {
                "title": "Historic Medina Mansion",
                "slug": "historic-medina-mansion",
                "description": "Grand traditional house in the Sousse Medina, featuring a stunning central courtyard.",
                "price": 1350000,
                "type": "house",
                "listing": "sale",
                "city": "Sousse",
                "country": "Tunisia",
                "bedrooms": 6,
                "bathrooms": 4,
                "area": 480,
                "image": "/static/seed-images/house.png",
                "agent_email": "k.jelassi@elite.tn",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Garden", "Sea View"],
                "latitude": 35.83,
                "longitude": 10.64
            },
            {
                "title": "Modern Tech Loft",
                "slug": "modern-tech-loft",
                "description": "State-of-the-art loft in Ghazela Technopark, fully automated and highly secure.",
                "price": 3800,
                "type": "apartment",
                "listing": "rent",
                "city": "Ghazela",
                "country": "Tunisia",
                "bedrooms": 2,
                "bathrooms": 2,
                "area": 145,
                "image": "/static/seed-images/apartment.png",
                "agent_email": "n.moussa@elite.tn",
                "owner_email": "h.kallel@elite.tn",
                "features": ["Smart Home", "High-speed Internet", "Gym", "Garage"],
                "latitude": 36.89,
                "longitude": 10.18
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
                description_vector=ai.get_embedding(p["description"])
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

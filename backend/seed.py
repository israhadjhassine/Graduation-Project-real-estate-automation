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
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
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
        head1 = models.User(email="j6r.chebbi6@gmail.com", full_name="Hedi Kallel", role="head_agent", hashed_password=auth.get_password_hash("managerpassword"))
        db.add(head1)
        
        db.commit()
        db.refresh(head1)

        # Sub-Agents (All managed by Hedi Kallel)
        agent1 = models.User(
            email="killer.chebbi@gmail.com", 
            full_name="Ahmed Trabelsi", 
            role="agent", 
            hashed_password=auth.get_password_hash("agentpassword"), 
            manager_id=head1.id
        )
        agent2 = models.User(email="s.dridi@elite.tn", full_name="Sonia Dridi", role="agent", hashed_password=auth.get_password_hash("agentpassword"), manager_id=head1.id)
        agent3 = models.User(email="k.jelassi@elite.tn", full_name="Karim Jelassi", role="agent", hashed_password=auth.get_password_hash("agentpassword"), manager_id=head1.id)
        agent4 = models.User(email="n.moussa@elite.tn", full_name="Nadine Moussa", role="agent", hashed_password=auth.get_password_hash("agentpassword"), manager_id=head1.id)
        
        db.add_all([agent1, agent2, agent3, agent4])
        
        # Client (for testing visits)
        client = models.User(email="ikaryo.chenji6@gmail.com", full_name="John Client", role="client", hashed_password=auth.get_password_hash("clientpassword"))
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
                "description": "This spectacular ultra-modern villa is situated on a private cliffside plot in the exclusive coastal enclave of Gammarth, offering breathtaking, unobstructed panoramic views of the Mediterranean Sea. The architectural design features clean, minimalist lines with expansive floor-to-ceiling glass facades that maximize natural lighting and seamlessly merge the indoor and outdoor living areas. Inside, the open-concept layout includes double-height ceilings, a state-of-the-art Italian chef's kitchen, and premium white marble flooring throughout. The outdoor oasis boasts a beautifully manicured landscaped garden surrounding an infinity swimming pool, creating a perfect sanctuary for family gatherings and high-end summer entertaining. For convenience and security, the property is equipped with a fully integrated smart home automation system controlling the lighting, climate, and security cameras, alongside a spacious multi-car garage. Located just minutes from Gammarth's finest beach clubs, gourmet restaurants, and a world-class marina, this mansion offers an unparalleled luxury lifestyle tailored for discerning buyers seeking a private coastal retreat.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Swimming Pool", "Sea View", "Smart Home", "Garage", "Garden"],
                "latitude": 36.9156,
                "longitude": 10.2915
            },
            {
                "title": "Blue Horizon Penthouse",
                "slug": "blue-horizon-penthouse",
                "description": "Perched high in the picturesque artistic village of Sidi Bou Said, this exceptional contemporary penthouse offers a sophisticated lifestyle overlooking the Gulf of Tunis. The residence boasts high-end Italian finishings, light oak hardwood flooring, and an expansive open-plan living and dining area designed to capture the brilliant Mediterranean light. Expansive sliding glass doors open onto a magnificent private wrap-around terrace, offering panoramic sea views that are perfect for sunset dinners or morning coffee. The master suite features an en-suite spa-like bathroom and a walk-in wardrobe. Residents enjoy exclusive access to a modern building gym equipped with cardio and strength-training machines. The building is serviced by a quiet, high-speed elevator providing direct access to the secure underground garage where two parking spaces are reserved for this unit. Situated in a peaceful neighborhood famed for its iconic blue-and-white architecture, local art galleries, and charming cafes, this penthouse offers an ideal combination of traditional Tunisian charm, security, and modern luxury living.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Sea View", "Elevator", "Gym", "Garage"],
                "latitude": 36.8706,
                "longitude": 10.3417
            },
            {
                "title": "Mediterranean Dream Estate",
                "slug": "mediterranean-dream-estate",
                "description": "Located in the highly sought-after area of Hammamet North, this majestic estate combines Moorish-inspired architectural details with modern luxury. The property is set on an expansive plot characterized by ancient olive groves, a private tennis court, and lush lawns. The grand entryway leads into a spacious layout with high arched ceilings, exquisite handmade tilework, and multiple light-filled lounges that open directly onto the outdoors. The heart of the outdoor space is a massive sparkling swimming pool surrounded by a stone patio and a meticulously landscaped Mediterranean garden, providing a tranquil oasis for relaxation and family fun. A secure, double-entry garage provides ample storage and parking. The estate offers total privacy while remaining highly accessible, situated just a short drive from pristine sandy beaches, local markets, and essential services. This property represents the ultimate vacation or permanent family residence for those who value space, privacy, and traditional Mediterranean elegance in a premium resort town.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Swimming Pool", "Garden", "Garage"],
                "latitude": 36.4000,
                "longitude": 10.6167
            },
            {
                "title": "Urban Oasis Lofts",
                "slug": "urban-oasis-lofts",
                "description": "This chic, industrial-style loft is situated in the vibrant heart of the Les Berges du Lac 2 business district, offering an ideal urban dwelling for young professionals and corporate executives. The loft features an open-concept design with exposed brick walls, polished concrete floors, double-height ceilings, and massive steel-framed windows that flood the entire space with natural light. The contemporary kitchen is equipped with top-tier integrated appliances, flowing effortlessly into the living area. Designed for the modern digital lifestyle, the loft comes fully wired with high-speed internet and features a state-of-the-art smart home system that allows residents to control lighting, climate, and keyless entry from their smartphones. Residents also benefit from access to a fully equipped building gym, perfect for maintaining a healthy routine. The property is exceptionally located within walking distance of multinational corporate offices, upscale cafes, fine dining restaurants, and the scenic lakefront promenade, providing the perfect blend of work, play, and lifestyle convenience in Tunis's premier commercial hub.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Smart Home", "Gym", "High-speed Internet"],
                "latitude": 36.8359,
                "longitude": 10.2367
            },
            {
                "title": "Golden Sands Villa",
                "slug": "golden-sands-villa",
                "description": "Nestled directly along the pristine coastline of Hammamet, this stunning beachfront villa offers an idyllic coastal lifestyle. The architectural design is a beautiful fusion of contemporary clean lines and traditional coastal elements, optimized to catch refreshing sea breezes. Inside, the sun-drenched living areas feature large windows, a stone fireplace, and a light color palette that mirrors the sandy beach outside. The ground floor bedroom suites enjoy direct access to the outdoor spaces, while the master suite offers a private balcony. The spacious outdoor area boasts a sparkling swimming pool and a verdant landscaped garden that leads directly to the sandy beach. A secure garage is integrated into the property, providing safe parking and storage for beach equipment. Perfect as a vacation retreat or a family home, this villa is located in a quiet residential area, yet is close to the lively tourist zone with its shops, restaurants, and historical sites.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Swimming Pool", "Garden", "Garage"],
                "latitude": 36.4,
                "longitude": 10.6
            },
            {
                "title": "Carthage Heritage House",
                "slug": "carthage-heritage-house",
                "description": "Embrace the history of Tunis in this grand historical mansion situated in the prestigious heart of Carthage. This extraordinary property showcases traditional Tunisian architectural craftsmanship, featuring magnificent white-and-black stone archways, ornate plaster carvings, and a beautiful central courtyard that serves as the heart of the home. Despite its historical character, the residence has been thoughtfully updated to include modern comforts, such as a comprehensive central heating system for the cooler winter months. The sprawling interior offers multiple formal reception rooms, seven spacious bedrooms, and six bathrooms, making it perfect for a large family or hosting diplomatic guests. Outside, a mature, walled garden filled with jasmine, citrus trees, and ancient pines provides a secure, private sanctuary. A spacious garage offers parking for several vehicles. Located in a prestigious and secure neighborhood, the villa is within walking distance of the ancient Roman ruins, select international schools, and local seaside cafes, offering a prestigious and culturally rich lifestyle.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Garden", "Garage", "Central Heating"],
                "latitude": 36.85,
                "longitude": 10.32
            },
            {
                "title": "Emerald Garden Apartment",
                "slug": "emerald-garden-apartment",
                "description": "Situated in one of the most desirable residential pockets of La Marsa, this bright and airy apartment offers a peaceful sanctuary overlooking the lush central park. The property features a modern architectural design with large windows that welcome natural light into every room, highlighting the clean wooden finishes and neutral color tones. The spacious living and dining area is perfect for family gatherings or entertaining guests, extending onto a covered balcony. Equipped with high-speed internet connectivity, the apartment is perfectly suited for remote work or streaming. The building offers premium amenities including a quiet, modern elevator and a secure basement garage with designated parking. The location is highly accessible, within a short stroll of local artisan bakeries, fashionable boutiques, the French high school, and the beautiful sandy beaches of La Marsa. This residence is perfect for families or expatriates seeking a balance of urban convenience, coastal lifestyle, and neighborhood tranquility.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["High-speed Internet", "Elevator", "Garage"],
                "latitude": 36.88,
                "longitude": 10.33
            },
            {
                "title": "Sapphire Bay Residence",
                "slug": "sapphire-bay-residence",
                "description": "Experience modern coastal living in this exceptionally designed apartment situated right on the Bizerte Corniche. The apartment's floor-to-ceiling windows frames a breathtaking, panoramic sea view, allowing residents to watch the boats pass by from the comfort of their living room or private balcony. The interior features a sleek kitchen, a spacious open-concept living area, and premium tiled floors. A fully integrated smart home automation system allows for effortless control of the climate, lighting, and security systems. The modern building offers direct access via a quiet elevator, making it highly accessible and convenient. Located in a vibrant neighborhood, the residence is close to local fish markets, cafes, and sandy beaches, making it an excellent vacation home or rental investment for those who appreciate the maritime charm of Bizerte.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Sea View", "Smart Home", "Elevator"],
                "latitude": 37.27,
                "longitude": 9.87
            },
            {
                "title": "Olive Grove Retreat",
                "slug": "olive-grove-retreat",
                "description": "This peaceful villa is located in a quiet, rural-suburban area of Nabeul, surrounded by beautiful olive groves and citrus trees. Designed with traditional architecture, the property features rustic stone wall accents, exposed wooden ceiling beams, and a charming brick fireplace in the spacious living room. A built-in central heating system ensures the villa remains warm and cozy during the winter months. The property boasts a large, private garden filled with mature olive trees and native plants, offering a quiet sanctuary for children to play and adults to relax. A secure garage is located at the front of the property. This retreat is perfect for families looking to escape the noise of the city while remaining within a short drive of Nabeul's renowned ceramic markets, local sandy beaches, and daily amenities.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Garden", "Garage", "Central Heating"],
                "latitude": 36.45,
                "longitude": 10.73
            },
            {
                "title": "Skyline Business Suite",
                "slug": "skyline-business-suite",
                "description": "This premium business suite is located in the prestigious Berges du Lac 1 commercial district, offering high-end accommodation for corporate executives and busy professionals. The apartment features a contemporary open-concept layout with premium marble floors, designer lighting, and floor-to-ceiling windows offering views of the city skyline. A state-of-the-art smart home system controls the automated blinds, lighting, and security. The building offers excellent lifestyle amenities, including a fully equipped modern gym, a quiet elevator, and a secure underground garage with designated parking spaces. Located near major corporate headquarters, embassies, high-end restaurants, and Tunis-Carthage Airport, this suite offers maximum convenience and prestige in the heart of the capital.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Smart Home", "Gym", "Garage", "Elevator"],
                "latitude": 36.84,
                "longitude": 10.2
            },
            {
                "title": "Jasmine Valley Estate",
                "slug": "jasmine-valley-estate",
                "description": "Perched on the hills of Ennasr, this upscale villa offers breathtaking panoramic views of the city of Tunis. The architecture is a modern take on the traditional Mediterranean villa, featuring clean white stucco walls, large arched windows, and spacious rooms that flow seamlessly into one another. The cozy living room features a fireplace and is connected to a central heating system that heats the entire home. The private terraced garden is planted with fragrant jasmine bushes and fruit trees, creating a quiet space to relax and enjoy the breeze. A secure garage provides safe parking and storage. Located in a family-friendly neighborhood, the villa is close to top schools, clinics, and the bustling commercial avenue of Ennasr 2 with its cafes and shopping centers.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Garage", "Garden", "Central Heating"],
                "latitude": 36.86,
                "longitude": 10.16
            },
            {
                "title": "Coral Reef Cottage",
                "slug": "coral-reef-cottage",
                "description": "This charming, rustic cottage is situated on a hillside near the pine forests and beautiful sandy beaches of Tabarka. Designed in a cozy traditional style with red-tiled roofs and local stone details, the cottage offers a warm and welcoming atmosphere. The open-plan living area features large windows that capture stunning sea views of the Mediterranean coastline and the historic Genoese fort. Outside, a lovely private garden filled with wildflowers and pine trees offers a peaceful spot for outdoor dining or relaxing in the sun. This cottage is an ideal vacation retreat or investment property for nature lovers who want to enjoy Tabarka's world-class diving sites, hiking trails, and championship golf course.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Garden", "Sea View"],
                "latitude": 36.95,
                "longitude": 8.75
            },
            {
                "title": "Ancient City Loft",
                "slug": "ancient-city-loft",
                "description": "This unique, beautifully restored loft is located in the historic heart of the Kairouan Medina. The design preserves the building's historical character, featuring high ceilings with original wooden beams, authentic handmade tiles, and traditional arched doorways. The loft has been updated with modern amenities, including high-speed internet, making it perfect for remote workers or history lovers looking for an authentic experience. The open living area is bright and spacious, with windows looking out over the quiet cobbled streets of the ancient city. Located just steps from the Great Mosque of Kairouan, traditional carpet markets, and local spice shops, this loft offers a unique lifestyle in one of Tunisia's most historic and cultural cities.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["High-speed Internet"],
                "latitude": 35.67,
                "longitude": 10.1
            },
            {
                "title": "Desert Rose Villa",
                "slug": "desert-rose-villa",
                "description": "This luxury villa in Tozeur features traditional yellow brick architecture, characteristic of the region, combined with modern upscale living. The villa's interior design uses local wood, natural stone, and desert colors, creating a cool and comfortable environment. The spacious layout includes three comfortable bedrooms, each with its own en-suite bathroom. The highlight of the property is the private oasis garden, featuring mature date palms, native desert plants, and a sparkling swimming pool, providing a perfect escape from the midday sun. A secure garage is located at the front of the villa. Located close to the city center and the palm groves, this villa is an exceptional vacation home or guest house for travelers looking to explore the Sahara.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Swimming Pool", "Garden", "Garage"],
                "latitude": 33.92,
                "longitude": 8.13
            },
            {
                "title": "Azure Coast Villa",
                "slug": "azure-coast-villa",
                "description": "This spectacular coastal villa is located in Kelibia, famous for having some of the most beautiful white-sand beaches in the Mediterranean. The modern architectural design features wide glass walls that offer breathtaking, panoramic sea views of the turquoise waters and the historic Kelibia Fort. Inside, the open-plan living areas are spacious and bright, with high-quality finishes and marble floors. The outdoor space is designed for luxury seaside living, featuring a private swimming pool, a spacious wooden deck, and a beautifully landscaped garden that leads down to the beach. This villa is a perfect vacation retreat or permanent home for large families looking to enjoy a premium beach lifestyle in a peaceful and scenic coastal town.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Sea View", "Swimming Pool", "Garden"],
                "latitude": 36.85,
                "longitude": 11.1
            },
            {
                "title": "Palm Grove Apartment",
                "slug": "palm-grove-apartment",
                "description": "Located in a peaceful residential area of Djerba, this traditional Djerbian-style apartment is set within a quiet, private palm grove. The architecture features traditional white dome roofs, thick walls that keep the interior naturally cool, and arched windows. Inside, the apartment offers a cozy layout with modern amenities, including high-speed internet, making it ideal for long-term stays or remote workers. The apartment opens onto a shared garden filled with olive trees and date palms, offering a peaceful space to relax. Located just a short drive from the beach, local craft markets, and authentic Djerbian restaurants, this apartment offers a unique and serene island lifestyle in one of Tunisia's most famous destinations.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Garden", "High-speed Internet"],
                "latitude": 33.87,
                "longitude": 10.85
            },
            {
                "title": "Roman Ruins View Apartment",
                "slug": "roman-ruins-view",
                "description": "This unique and spacious apartment in El Jem offers a direct, unobstructed view of the world-famous Roman amphitheater, a UNESCO World Heritage site. The apartment features a modern design with large windows that flood the living space with natural light. The layout includes two comfortable bedrooms, a modern kitchen, and a spacious living area that opens onto a balcony facing the ancient monument. The building offers convenient amenities, including a modern elevator and a secure basement garage with a designated parking space. Located in the center of El Jem, the apartment is within walking distance of local restaurants, museums, and train stations, making it an excellent investment for cultural tourism or a unique residence.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Elevator", "Garage"],
                "latitude": 35.3,
                "longitude": 10.7
            },
            {
                "title": "Mountain Peak Lodge",
                "slug": "mountain-peak-lodge",
                "description": "This rustic wooden lodge is located in the beautiful oak forests of the Ain Draham mountains, offering a cozy mountain retreat. The lodge's interior is decorated with natural wood panels, exposed stone walls, and a large brick fireplace, creating a warm and inviting atmosphere. A built-in central heating system ensures the entire lodge remains warm during the snowy winter months. The property features a private garden surrounded by tall pine trees, providing a quiet space to enjoy the clean mountain air. Located near scenic hiking trails and natural springs, this lodge is the perfect winter getaway or vacation rental for outdoor lovers looking to experience the unique nature of northwestern Tunisia.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Central Heating", "Garden"],
                "latitude": 36.78,
                "longitude": 8.68
            },
            {
                "title": "Sun-Kissed Bungalow",
                "slug": "sun-kissed-bungalow",
                "description": "This charming bungalow is located in Mahdia, just steps away from some of the most beautiful and clear turquoise waters in Tunisia. The bungalow features a traditional coastal style with white stucco walls, blue window frames, and arched doorways. The interior is bright and airy, with large windows offering sea views from the living room and master bedroom. The property includes a private garden filled with native coastal plants and flowers, offering a quiet space for outdoor dining and relaxation. Located in a peaceful neighborhood, the bungalow is close to the historic Medina of Mahdia, local fish restaurants, and daily services, making it a perfect retirement home or family vacation bungalow.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Sea View", "Garden"],
                "latitude": 35.5,
                "longitude": 11.06
            },
            {
                "title": "Lavender Fields Estate",
                "slug": "lavender-fields-estate",
                "description": "This impressive countryside estate is located in Tebourba, surrounded by lavender fields and green hills. The modern farmhouse architecture features stone walls, vaulted ceilings, and large glass windows that offer peaceful views of the countryside. The villa is equipped with a modern smart home system, allowing residents to control the climate, lighting, and security from their phones. The property boasts a large, private garden filled with lavender, olive trees, and rosemary, providing a quiet and scenic outdoor space. A spacious garage provides parking and storage. This estate is an ideal permanent residence or weekend home for families looking to enjoy the peace of the countryside while remaining within an hour's drive of Tunis.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Garden", "Garage", "Smart Home"],
                "latitude": 36.83,
                "longitude": 9.84
            },
            {
                "title": "Old Port Studio",
                "slug": "old-port-studio",
                "description": "This cozy and stylish studio apartment is located in the historic Old Port area of Bizerte. The studio has been fully renovated, featuring exposed stone walls, modern furniture, and large windows that offer views of the historic harbor and the old fortress. Equipped with high-speed internet, the studio is perfect for digital nomads, young couples, or travelers looking for a comfortable base to explore the city. The location is highly convenient, within walking distance of the fish market, traditional cafes, and local beaches. This studio offers a unique opportunity to live in one of the most historic and picturesque maritime neighborhoods in Bizerte, combining historical charm with modern comfort.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Sea View", "High-speed Internet"],
                "latitude": 37.28,
                "longitude": 9.88
            },
            {
                "title": "Central Park Residence",
                "slug": "central-park-residence",
                "description": "This modern apartment is located in a quiet and green residential neighborhood of Ariana, perfect for family living. The interior is spacious and bright, featuring large windows, hardwood floors, and a modern kitchen. The apartment is equipped with a smart home automation system, allowing residents to easily control the lighting and climate. The building offers excellent conveniences, including a quiet elevator and a secure basement garage with a private parking space. Located close to the Ennasr commercial area, top-rated schools, parks, and daily amenities, this apartment offers the perfect balance of convenience and residential comfort for families looking for a high-quality home in Ariana.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Elevator", "Garage", "Smart Home"],
                "latitude": 36.86,
                "longitude": 10.19
            },
            {
                "title": "Historic Medina Mansion",
                "slug": "historic-medina-mansion",
                "description": "This grand traditional mansion is located in the historic Sousse Medina, a UNESCO World Heritage site. The architecture features a beautiful central courtyard with marble columns, traditional arched doorways, and hand-painted Tunisian tiles. The mansion includes six spacious bedrooms, multiple traditional seating rooms, and a large roof terrace offering stunning sea views of the Gulf of Sousse and the port. Outside, a private walled garden with citrus trees offers a quiet escape from the busy streets. Located just steps from the historic souks, museums, and the beach, this mansion is an exceptional property for a boutique hotel investment or a grand private home filled with history and character.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
                "features": ["Garden", "Sea View"],
                "latitude": 35.83,
                "longitude": 10.64
            },
            {
                "title": "Modern Tech Loft",
                "slug": "modern-tech-loft",
                "description": "This state-of-the-art loft is located in the Ghazela Technopark area, Tunisia's leading technology hub. The loft is designed for tech-savvy professionals, featuring a fully automated smart home system, high-speed internet, and modern industrial interior design with high ceilings and large windows. The spacious layout includes two modern bedrooms, two bathrooms, and an open-concept living area. Residents enjoy excellent building amenities, including a private gym, a secure underground garage with designated parking, and 24/7 security. Located close to university campuses, research centers, and tech companies, this loft offers an ideal modern lifestyle combining comfort, security, and technology in a growing innovation district.",
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
                "owner_email": "j6r.chebbi6@gmail.com",
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
                description_vector=ai.generate_property_embedding(p)
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

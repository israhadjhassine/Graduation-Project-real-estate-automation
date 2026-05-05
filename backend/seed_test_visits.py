import sys
import os
from datetime import datetime, timedelta

# Add the current directory to sys.path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Visit, Property, User

def seed_visit():
    db = SessionLocal()
    try:
        # 1. Setup Ocean Breeze Mansion for Ahmed (ID 105)
        ocean_breeze = db.query(Property).filter(Property.title == 'Ocean Breeze Mansion').first()
        ahmed = db.query(User).filter(User.id == 105).first()
        
        # 2. Setup Blue Horizon Penthouse for Sonia (ID 106)
        blue_horizon = db.query(Property).filter(Property.title == 'Blue Horizon Penthouse').first()
        sonia = db.query(User).filter(User.id == 106).first()

        if not (ocean_breeze and ahmed and blue_horizon and sonia):
            print("❌ Could not find all required properties or agents.")
            return

        # Ensure properties are assigned to the right agents
        ocean_breeze.agent_id = ahmed.id
        blue_horizon.agent_id = sonia.id
        db.commit()

        # Create Overlapping Visits (Today at 10:00 AM)
        today_10am = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        
        visit1 = Visit(
            property_id=ocean_breeze.id,
            agent_id=ahmed.id,
            visit_date=today_10am,
            status="scheduled"
        )

        visit2 = Visit(
            property_id=blue_horizon.id,
            agent_id=sonia.id,
            visit_date=today_10am,
            status="scheduled"
        )

        # 3. Create another visit for testing minutes (4:30 PM)
        today_430pm = datetime.now().replace(hour=16, minute=30, second=0, microsecond=0)
        visit3 = Visit(
            property_id=ocean_breeze.id,
            agent_id=ahmed.id,
            visit_date=today_430pm,
            status="scheduled"
        )

        db.add(visit1)
        db.add(visit2)
        db.add(visit3)
        db.commit()
        
        print(f"✅ Success! Seeded overlapping visits for testing:")
        print(f"   - Ahmed: Ocean Breeze Mansion @ {visit1.visit_date.strftime('%H:%M')}")
        print(f"   - Sonia: Blue Horizon Penthouse @ {visit2.visit_date.strftime('%H:%M')} (OVERLAP)")
        print(f"   - Ahmed: Ocean Breeze Mansion @ {visit3.visit_date.strftime('%H:%M')}")
        
    except Exception as e:
        print(f"❌ Error seeding visits: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_visit()

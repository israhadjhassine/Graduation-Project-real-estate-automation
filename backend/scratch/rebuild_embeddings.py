import sys
import os

# Add parent directory (backend) to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import joinedload
from database import SessionLocal
import models
from services import ai

def rebuild_embeddings():
    print("🔄 Connecting to database...")
    db = SessionLocal()
    try:
        print("🔍 Fetching all properties...")
        properties = db.query(models.Property).options(
            joinedload(models.Property.features)
        ).all()
        
        total = len(properties)
        print(f"📋 Found {total} properties to update.")
        
        for idx, prop in enumerate(properties, 1):
            print(f"[{idx}/{total}] Rebuilding embedding for: {prop.title} (ID: {prop.id})...")
            embedding = ai.generate_property_embedding(prop)
            if embedding:
                prop.description_vector = embedding
                print(f"   ✅ Success.")
            else:
                print(f"   ❌ Failed to generate embedding.")
                
        print("💾 Saving changes to database...")
        db.commit()
        print("🎉 Successfully rebuilt all property search embeddings!")
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    rebuild_embeddings()

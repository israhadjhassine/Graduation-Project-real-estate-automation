import models, database, auth
from utils import embeddings
from sqlalchemy.orm import Session

db = next(database.get_db())
properties = db.query(models.Property).all()

print(f"Found {len(properties)} properties. Updating vectors...")

for prop in properties:
    print(f"Generating vector for: {prop.title}")
    vector = embeddings.get_embedding(prop.description)
    if vector:
        prop.description_vector = vector
        db.commit()
        print(f"✅ Updated {prop.title}")
    else:
        print(f"❌ Failed to generate vector for {prop.title}")

print("Done!")

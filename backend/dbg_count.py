import models, database
from sqlalchemy.orm import Session

db = next(database.get_db())
count = db.query(models.Property).count()
available = db.query(models.Property).filter(models.Property.status == 'available').count()
print(f"Total properties: {count}")
print(f"Available properties: {available}")

import auth, models, database
from sqlalchemy.orm import Session

db = next(database.get_db())
user = db.query(models.User).filter(models.User.email == 'israhadjhassine@gmail.com').first()
if user:
    print(f"User found: {user.email}")
    is_match = auth.verify_password("123", user.hashed_password)
    print(f"Password '123' matches: {is_match}")
else:
    print("User not found!")

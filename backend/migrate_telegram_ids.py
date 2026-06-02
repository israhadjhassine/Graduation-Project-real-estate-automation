import os
import sys

# Ensure backend directory is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
import models
from utils.security import encrypt_telegram_id, decrypt_telegram_id

def migrate():
    db = SessionLocal()
    try:
        # 1. Migrate Users
        users = db.query(models.User).filter(models.User.telegram_chat_id.isnot(None)).all()
        updated_users_count = 0
        for user in users:
            raw_val = user.telegram_chat_id
            if not raw_val:
                continue
            
            # If decrypting returns the value itself, it means decryption failed (legacy raw value)
            decrypted = decrypt_telegram_id(raw_val)
            if decrypted == raw_val:
                encrypted = encrypt_telegram_id(raw_val)
                user.telegram_chat_id = encrypted
                updated_users_count += 1
                print(f"User {user.id} ({user.email}): Encrypted telegram_chat_id {raw_val} -> {encrypted}")
        
        # 2. Migrate Visits
        visits = db.query(models.Visit).filter(models.Visit.telegram_chat_id.isnot(None)).all()
        updated_visits_count = 0
        for visit in visits:
            raw_val = visit.telegram_chat_id
            if not raw_val:
                continue
            
            decrypted = decrypt_telegram_id(raw_val)
            if decrypted == raw_val:
                encrypted = encrypt_telegram_id(raw_val)
                visit.telegram_chat_id = encrypted
                updated_visits_count += 1
                print(f"Visit {visit.id} (Property {visit.property_id}): Encrypted telegram_chat_id {raw_val} -> {encrypted}")
        
        if updated_users_count > 0 or updated_visits_count > 0:
            db.commit()
            print(f"Migration completed successfully. Encrypted {updated_users_count} users and {updated_visits_count} visits.")
        else:
            print("No raw telegram chat IDs found. Database is already fully encrypted.")
            
    except Exception as e:
        db.rollback()
        print(f"Migration failed: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    migrate()

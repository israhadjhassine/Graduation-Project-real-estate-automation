from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import models, schemas, database, auth
from services import email
from repositories.user_repository import UserRepository

router = APIRouter(
    tags=["Authentication"]
)

@router.post("/auth/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """Creates a new user account."""
    db_user = UserRepository.get_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = auth.get_password_hash(user.password)
    new_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_pwd,
        role=user.role,
        manager_id=user.manager_id
    )
    return UserRepository.create(db, new_user)

@router.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    """Standard OAuth2 Login flow."""
    user = UserRepository.get_by_email(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account has been deactivated. Please contact your manager.",
        )
    
    access_token = auth.create_access_token(data={"sub": user.email, "role": user.role, "user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/auth/me", response_model=schemas.User)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    """Returns currently authenticated user info."""
    return current_user

@router.put("/auth/profile", response_model=schemas.User)
def update_profile(
    user_update: schemas.UserUpdate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Updates profile info."""
    if user_update.full_name: 
        current_user.full_name = user_update.full_name
    if user_update.email:
        if current_user.email != user_update.email:
            existing = UserRepository.get_by_email(db, user_update.email)
            if existing: 
                raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = user_update.email
    
    if user_update.phone_number: 
        current_user.phone_number = user_update.phone_number
    if user_update.google_calendar_id is not None: 
        current_user.google_calendar_id = user_update.google_calendar_id
    
    UserRepository.commit(db)
    UserRepository.refresh(db, current_user)
    return current_user

@router.put("/auth/password")
def update_password(
    passwords: schemas.PasswordUpdate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Updates password."""
    if not auth.verify_password(passwords.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    current_user.hashed_password = auth.get_password_hash(passwords.new_password)
    UserRepository.commit(db)
    return {"message": "Password updated successfully"}

@router.get("/agents/{agent_id}/calendar")
def get_agent_calendar(agent_id: int, db: Session = Depends(database.get_db)):
    """Returns agent calendar ID."""
    agent = UserRepository.get_agent_by_id(db, agent_id)
    if not agent: 
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {
        "agent_id": agent.id,
        "full_name": agent.full_name,
        "google_calendar_id": agent.google_calendar_id,
        "email": agent.email
    }

@router.get("/agency/staff", response_model=List[schemas.User])
def get_team_staff(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Returns sub-agents."""
    if current_user.role == "admin":
        return UserRepository.get_all_agents(db)
    return UserRepository.get_team_staff(db, current_user.id)

@router.patch("/agency/staff/{agent_id}/toggle-status")
def toggle_sub_agent_status(
    agent_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    """Toggles sub-agent status."""
    agent = UserRepository.get_by_id(db, agent_id)
    if not agent: 
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if current_user.role == "head_agent" and agent.manager_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    agent.is_active = not agent.is_active
    UserRepository.commit(db)

    # Send status update email
    if agent.email:
        background_tasks.add_task(
            email.send_account_status_email,
            user_email=agent.email,
            user_name=agent.full_name,
            is_active=agent.is_active,
            manager_name=current_user.full_name
        )

    return {"message": f"Agent {'enabled' if agent.is_active else 'disabled'}", "is_active": agent.is_active}

@router.get("/admin/users", response_model=List[schemas.User])
def get_all_users(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["admin"]))
):
    """Admin view all staff users."""
    return UserRepository.get_all_staff(db)

@router.post("/admin/users", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user_admin(
    user_in: schemas.UserCreateAdmin,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["admin", "head_agent"]))
):
    """Create staff accounts."""
    db_user = UserRepository.get_by_email(db, user_in.email)
    if db_user: 
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = auth.get_password_hash(user_in.password)
    new_user = models.User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_pwd,
        role=user_in.role,
        phone_number=user_in.phone_number,
        manager_id=user_in.manager_id
    )
    return UserRepository.create(db, new_user)

@router.patch("/admin/users/{user_id}/toggle-status")
def toggle_user_status(
    user_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["admin"]))
):
    """Toggle any user status."""
    user = UserRepository.get_by_id(db, user_id)
    if not user: 
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id: 
        raise HTTPException(status_code=400, detail="Cannot disable yourself")
    
    user.is_active = not user.is_active
    UserRepository.commit(db)

    # Send status update email
    if user.email:
        background_tasks.add_task(
            email.send_account_status_email,
            user_email=user.email,
            user_name=user.full_name,
            is_active=user.is_active,
            manager_name=current_user.full_name
        )

    return {"message": f"User {'enabled' if user.is_active else 'disabled'} successfully", "is_active": user.is_active}

@router.get("/admin/head_agents", response_model=List[schemas.User])
def get_head_agents(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.RoleChecker(["admin"]))
):
    """Returns all Head Agents."""
    return UserRepository.get_head_agents(db)

@router.post("/auth/telegram/generate-code", response_model=schemas.TelegramCodeResponse)
def generate_telegram_code(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Generates a secure 6-digit pairing code for the logged-in user."""
    import random
    from datetime import datetime, timedelta

    # Delete any existing pairing code for this user
    db.query(models.TelegramPairingCode).filter(models.TelegramPairingCode.user_id == current_user.id).delete()
    
    # Generate unique 6-digit code
    code = f"{random.randint(100000, 999999)}"
    # Ensure uniqueness in the pairing code table
    while db.query(models.TelegramPairingCode).filter(models.TelegramPairingCode.code == code).first():
        code = f"{random.randint(100000, 999999)}"
        
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    pairing_code = models.TelegramPairingCode(
        user_id=current_user.id,
        code=code,
        expires_at=expires_at
    )
    
    db.add(pairing_code)
    db.commit()
    
    return {
        "code": code,
        "expires_in_seconds": 600
    }

@router.post("/auth/telegram/pair", response_model=schemas.TelegramPairingSuccessResponse)
def pair_telegram_account(
    payload: schemas.TelegramPairRequest,
    db: Session = Depends(database.get_db)
):
    """Links telegram_chat_id to user associated with the pairing code. (Called by n8n bot workflow)"""
    from datetime import datetime

    pairing_record = db.query(models.TelegramPairingCode).filter(models.TelegramPairingCode.code == payload.code).first()
    if not pairing_record:
        raise HTTPException(status_code=400, detail="Invalid pairing code.")
        
    if pairing_record.expires_at < datetime.utcnow():
        db.delete(pairing_record)
        db.commit()
        raise HTTPException(status_code=400, detail="Pairing code has expired.")
        
    user = db.query(models.User).filter(models.User.id == pairing_record.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User associated with code not found.")
        
    # Unlink any other user who already has this telegram_chat_id to prevent unique constraint failures
    existing_linked_users = db.query(models.User).filter(models.User.telegram_chat_id == payload.telegram_chat_id).all()
    for elu in existing_linked_users:
        elu.telegram_chat_id = None
        
    user.telegram_chat_id = payload.telegram_chat_id
    db.delete(pairing_record)
    db.commit()
    db.refresh(user)
    
    return {
        "status": "success",
        "user_name": user.full_name,
        "email": user.email
    }

@router.post("/auth/telegram/disconnect")
def disconnect_telegram_account(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Unlinks telegram_chat_id from the authenticated user."""
    current_user.telegram_chat_id = None
    db.commit()
    return {"message": "Telegram account disconnected successfully."}

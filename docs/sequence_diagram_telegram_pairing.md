# Sequence Diagram — Telegram Account Pairing (Authentication)

This document details the sequence of interactions for secure Telegram account pairing. This process maps a logged-in user's web account to their Telegram profile using a temporary 6-digit verification code, allowing the AI smart agent to recognize the client's identity for RAG search and visit bookings.

## 📌 Workflow Overview

1. **Verification Code Generation**:
   - The user requests a pairing code from the Profile page.
   - The backend deletes any obsolete pairing codes for the user, generates a secure 6-digit random code, saves it with a 10-minute expiration, and returns it.
2. **Deep Link Handoff**:
   - The Profile page starts a countdown timer and displays the code.
   - When the user clicks "Open Telegram Chat", the frontend opens a Telegram deep link formatting the start parameter: `/start pair_<code>`.
3. **Identity Verification & Mapping**:
   - The Telegram bot receives the `/start` command containing the code and triggers the n8n Smart Agent workflow.
   - The Smart Agent parses the code and sends it with the Telegram Chat ID to the FastAPI `/auth/telegram/pair` endpoint.
   - The backend validates the code and links the `telegram_chat_id` to the matching `UserModel`. It also safeguards uniqueness by resetting any existing user records using this ID.
   - Once success is confirmed, n8n replies to the user on Telegram confirming the link.

---

## 📊 Mermaid Representation

```mermaid
sequenceDiagram
    autonumber
    actor ActorUser as User
    participant ProfilePage as ProfilePage (profile.vue)
    participant Telegram as Telegram
    participant SmartAgent as SmartAgent (n8n)
    participant AuthController as AuthController (FastAPI)
    participant UserModel as UserModel (DB/Repo)

    ActorUser->>ProfilePage: generatePairingCode()
    activate ProfilePage

    ProfilePage->>AuthController: generate_telegram_code(db, current_user)
    activate AuthController

    Note over AuthController: db.query(models.TelegramPairingCode).filter().delete()
    Note over AuthController: Generate unique 6-digit code
    Note over AuthController: db.add(pairing_code)
    Note over AuthController: db.commit()

    AuthController-->>ProfilePage: codeResponse(code="592108", expires_in_seconds=600)
    deactivate AuthController

    ProfilePage->>ProfilePage: startCountdown(expires_in_seconds=600)
    Note over ProfilePage: Displays pairing code "592 108" & countdown timer

    ActorUser->>ProfilePage: Click "Open Telegram Chat" button
    Note over ProfilePage: Opens https://t.me/Pfe_rea_bot?start=pair_592108

    ActorUser->>Telegram: /start pair_592108
    activate Telegram

    Telegram->>SmartAgent: onTelegramUpdate(update(text="/start pair_592108", chat_id="12345"))
    activate SmartAgent

    Note over SmartAgent: parse_pairing_command(text="/start pair_592108") -> code="592108"

    SmartAgent->>AuthController: pair_telegram_account(TelegramPairRequest(code="592108", telegram_chat_id="12345"), db)
    activate AuthController

    Note over AuthController: db.query(models.TelegramPairingCode).filter(code == "592108").first()

    alt invalid or expired code
        AuthController-->>SmartAgent: HTTPException(400, "Invalid or expired code.")
        SmartAgent-->>Telegram: sendTelegramResponse(chat_id="12345", error_message)
        Note over Telegram: Displays error message to user
    else valid code
        Note over AuthController: encrypt_telegram_id("12345") -> encrypted_chat_id
        AuthController->>UserModel: db.query(models.User).filter(telegram_chat_id == encrypted_chat_id).all()
        activate UserModel
        UserModel-->>AuthController: existing_linked_users
        
        AuthController->>UserModel: update existing_linked_users (set telegram_chat_id = None)
        
        AuthController->>UserModel: db.query(models.User).filter(id == pairing_record.user_id).first()
        UserModel-->>AuthController: user(id=1, full_name="Jesse", email="jesse@example.com")
        deactivate UserModel
        
        Note over AuthController: user.telegram_chat_id = encrypted_chat_id
        Note over AuthController: db.delete(pairing_record)
        Note over AuthController: db.commit()
        Note over AuthController: db.refresh(user)
        
        AuthController-->>SmartAgent: TelegramPairingSuccessResponse(status="success", user_name="Jesse", email="jesse@example.com")
        deactivate AuthController
        
        SmartAgent-->>Telegram: sendTelegramResponse(chat_id="12345", success_message="Jesse, your account is successfully linked!")
        deactivate SmartAgent
        
        Note over Telegram: Displays success message to user
        deactivate Telegram
    end

    deactivate ProfilePage
```

---

## 📊 PlantUML Representation

To render this diagram using PlantUML, you can use the code below:

```plantuml
@startuml
autonumber

actor "User" as ActorUser
boundary ProfilePage
boundary Telegram
control SmartAgent
control AuthController
entity UserModel

ActorUser -> ProfilePage : generatePairingCode()
activate ProfilePage

ProfilePage -> AuthController : generate_telegram_code(db, current_user)
activate AuthController

AuthController -> AuthController : db.query(models.TelegramPairingCode).filter(user_id == current_user.id).delete()
AuthController -> AuthController : random.randint(100000, 999999)
note over AuthController : Generates code e.g. "592108"
AuthController -> AuthController : db.add(pairing_code)
AuthController -> AuthController : db.commit()

AuthController --> ProfilePage : codeResponse(code="592108", expires_in_seconds=600)
deactivate AuthController

ProfilePage -> ProfilePage : startCountdown(expires_in_seconds=600)
note over ProfilePage : Displays pairing code "592 108" & countdown timer

ActorUser -> ProfilePage : Click "Open Telegram Chat" button
note over ProfilePage : Opens https://t.me/Pfe_rea_bot?start=pair_592108

ActorUser -> Telegram : /start pair_592108
activate Telegram

Telegram -> SmartAgent : onTelegramUpdate(update(text="/start pair_592108", chat_id="12345"))
activate SmartAgent

SmartAgent -> SmartAgent : parse_pairing_command(text="/start pair_592108")
note over SmartAgent : Extracts code="592108"

SmartAgent -> AuthController : pair_telegram_account(TelegramPairRequest(code="592108", telegram_chat_id="12345"), db)
activate AuthController

AuthController -> AuthController : db.query(models.TelegramPairingCode).filter(code == "592108").first()
note over AuthController : Returns pairing_record(user_id=1, expires_at=...)

alt invalid or expired code
    AuthController --> SmartAgent : HTTPException(status_code=400, detail="Invalid or expired code.")
    SmartAgent --> Telegram : sendTelegramResponse(chat_id="12345", error_message)
    note over Telegram : Displays error message to user
else valid code
    AuthController -> AuthController : encrypt_telegram_id("12345") -> encrypted_chat_id
    AuthController -> UserModel : db.query(models.User).filter(telegram_chat_id == encrypted_chat_id).all()
    activate UserModel
    UserModel --> AuthController : existing_linked_users
    
    AuthController -> UserModel : update existing_linked_users (set telegram_chat_id = None)
    
    AuthController -> UserModel : db.query(models.User).filter(id == pairing_record.user_id).first()
    UserModel --> AuthController : user(id=1, full_name="Jesse", email="jesse@example.com")
    deactivate UserModel
    
    AuthController -> AuthController : user.telegram_chat_id = encrypted_chat_id
    AuthController -> AuthController : db.delete(pairing_record)
    AuthController -> AuthController : db.commit()
    AuthController -> AuthController : db.refresh(user)
    
    AuthController --> SmartAgent : TelegramPairingSuccessResponse(status="success", user_name="Jesse", email="jesse@example.com")
    deactivate AuthController
    
    SmartAgent --> Telegram : sendTelegramResponse(chat_id="12345", success_message="Jesse, your account is successfully linked!")
    deactivate SmartAgent
    
    note over Telegram : Displays success message to user
    deactivate Telegram
end

deactivate ProfilePage
@enduml
```

---

## 🛠️ Key Implementation Details

* **Frontend Pairing Page**: Located in [profile.vue](file:///c:/Users/jesse/Desktop/study/iset_me/terminal/stage_pfe/real-estate-automation/real-estate-automation/frontend/app/pages/profile.vue#L81-L190). The button executes `generatePairingCode()` to fetch a code from the backend and launches a countdown timer tracking the lifespan of the pairing token.
* **Backend Verification Endpoint**: Found in [backend/routers/auth.py](file:///c:/Users/jesse/Desktop/study/iset_me/terminal/stage_pfe/real-estate-automation/real-estate-automation/backend/routers/auth.py#L216-L285). The `/auth/telegram/generate-code` endpoint issues new pairing records while unlinking stale credentials. The `/auth/telegram/pair` verifies code parity, ensures single-client mapping consistency, and registers the telegram handle to the client's `UserModel`.

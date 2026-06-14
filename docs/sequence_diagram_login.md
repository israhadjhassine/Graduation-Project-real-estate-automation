# Sequence Diagram — User Login

This document details the sequence of interactions between the Visitor/Staff Client, the NuxtJS Frontend, the Pinia Auth Store, the FastAPI Backend, the authentication security module, and the PostgreSQL database during the user login flow.

## 📌 Workflow Overview

1. **User Action**: The user fills in credentials and clicks "Sign In", triggering the form submit handler.
2. **State Store Action**: The frontend Pinia store formats credentials and makes an async HTTP POST request to the login endpoint.
3. **Credentials Lookup & Verification**: 
   - The backend retrieves the user via the `UserRepository`.
   - The password hash is verified using `pwd_context` helpers.
   - The account status (`is_active`) is verified.
4. **Token Generation**: A JWT access token containing the sub (email), role, and user ID is generated and returned to the client.
5. **Session Bootstrap**: The store persists the token in local storage, executes an async call to retrieve user profile data, and navigates the user to their role-specific dashboard.

---

```mermaid
sequenceDiagram
    autonumber
    actor Client as Visitor / Staff User
    participant LoginPage as LoginPage (login.vue)
    participant useAuthStore as useAuthStore (auth.ts)
    participant AuthRouter as AuthRouter (routers/auth.py)
    participant auth as auth (auth.py)
    participant UserRepository as UserRepository (user_repository.py)
    participant Database as PostgreSQL (db: Session)

    Client->>LoginPage: handleLogin()
    activate LoginPage
    
    LoginPage->>useAuthStore: login(email, password)
    activate useAuthStore
    
    useAuthStore->>AuthRouter: login(form_data)
    activate AuthRouter
    
    AuthRouter->>UserRepository: get_by_email(db, form_data.username)
    activate UserRepository
    
    UserRepository->>Database: query(User).filter(User.email == email).first()
    activate Database
    Database-->>UserRepository: db_user
    deactivate Database
    
    UserRepository-->>AuthRouter: user
    deactivate UserRepository

    alt User not found or password verification fails
        opt user exists
            AuthRouter->>auth: verify_password(password, hashed_password)
            activate auth
            auth-->>AuthRouter: false
            deactivate auth
        end
        AuthRouter-->>useAuthStore: HTTPException(status_code=401, detail="Incorrect email or password")
        useAuthStore-->>LoginPage: error
        LoginPage-->>Client: showErrorToast()
        
    else Account is deactivated (user.is_active is False)
        AuthRouter->>auth: verify_password(password, hashed_password)
        activate auth
        auth-->>AuthRouter: true
        deactivate auth
        
        AuthRouter-->>useAuthStore: HTTPException(status_code=401, detail="This account has been deactivated...")
        useAuthStore-->>LoginPage: error
        LoginPage-->>Client: showErrorToast()
        
    else Valid credentials and active account
        AuthRouter->>auth: verify_password(password, hashed_password)
        activate auth
        auth-->>AuthRouter: true
        deactivate auth
        
        AuthRouter->>auth: create_access_token(data={"sub": user.email, ...})
        activate auth
        auth-->>AuthRouter: access_token
        deactivate auth
        
        AuthRouter-->>useAuthStore: token_response ({"access_token": token, "token_type": "bearer"})
        deactivate AuthRouter
        
        opt Token received successfully
            useAuthStore->>useAuthStore: fetchUser()
            activate useAuthStore
            
            useAuthStore->>AuthRouter: get_me(current_user)
            activate AuthRouter
            
            AuthRouter->>auth: get_current_user(token, db)
            activate auth
            
            auth->>auth: jwt.decode(token, SECRET_KEY, ...)
            
            auth->>Database: query(User).filter(User.email == token_data.email).first()
            activate Database
            Database-->>auth: user_row
            deactivate Database
            
            auth-->>AuthRouter: user
            deactivate auth
            
            AuthRouter-->>useAuthStore: current_user
            deactivate AuthRouter
            
            deactivate useAuthStore
        end
        
        useAuthStore-->>LoginPage: user
        deactivate useAuthStore
        
        alt auth.isAdmin is true
            LoginPage->>LoginPage: navigateTo('/admin')
        else auth.isHeadAgent is true
            LoginPage->>LoginPage: navigateTo('/agency')
        else auth.isAgent is true
            LoginPage->>LoginPage: navigateTo('/agent')
        else Default / Client User
            LoginPage->>LoginPage: navigateTo('/')
        end
        
        LoginPage-->>Client: dashboard page rendered
    end
    deactivate LoginPage
```

---

## 📊 PlantUML Representation

To render this diagram using PlantUML, you can use the code below:

```plantuml
@startuml
autonumber

actor "Visitor / Staff User" as Client
participant "LoginPage (login.vue)" as LoginPage
participant "useAuthStore (auth.ts)" as useAuthStore
participant "AuthRouter (routers/auth.py)" as AuthRouter
participant "auth (auth.py)" as auth
participant "UserRepository (user_repository.py)" as UserRepository
database "PostgreSQL (db: Session)" as Database

Client -> LoginPage : handleLogin()
activate LoginPage

LoginPage -> useAuthStore : login(email, password)
activate useAuthStore

useAuthStore -> AuthRouter : login(form_data)
activate AuthRouter

AuthRouter -> UserRepository : get_by_email(db, form_data.username)
activate UserRepository

UserRepository -> Database : query(User).filter(User.email == email).first()
activate Database
Database --> UserRepository : db_user
deactivate Database

UserRepository --> AuthRouter : user
deactivate UserRepository

alt User not found or password verification fails
    opt user exists
        AuthRouter -> auth : verify_password(password, hashed_password)
        activate auth
        auth --> AuthRouter : false
        deactivate auth
    end
    AuthRouter --> useAuthStore : HTTPException(status_code=401, detail="Incorrect email or password")
    useAuthStore --> LoginPage : error
    LoginPage --> Client : showErrorToast()

else Account is deactivated (user.is_active is False)
    AuthRouter -> auth : verify_password(password, hashed_password)
    activate auth
    auth --> AuthRouter : true
    deactivate auth
    
    AuthRouter --> useAuthStore : HTTPException(status_code=401, detail="This account has been deactivated...")
    useAuthStore --> LoginPage : error
    LoginPage --> Client : showErrorToast()

else Valid credentials and active account
    AuthRouter -> auth : verify_password(password, hashed_password)
    activate auth
    auth --> AuthRouter : true
    deactivate auth
    
    AuthRouter -> auth : create_access_token(data={"sub": user.email, ...})
    activate auth
    auth --> AuthRouter : access_token
    deactivate auth
    
    AuthRouter --> useAuthStore : token_response ({"access_token": token, "token_type": "bearer"})
    deactivate AuthRouter
    
    opt Token received successfully
        useAuthStore -> useAuthStore : fetchUser()
        activate useAuthStore
        
        useAuthStore -> AuthRouter : get_me(current_user)
        activate AuthRouter
        
        AuthRouter -> auth : get_current_user(token, db)
        activate auth
        
        auth -> auth : jwt.decode(token, SECRET_KEY, ...)
        
        auth -> Database : query(User).filter(User.email == token_data.email).first()
        activate Database
        Database --> auth : user_row
        deactivate Database
        
        auth --> AuthRouter : user
        deactivate auth
        
        AuthRouter --> useAuthStore : current_user
        deactivate AuthRouter
        deactivate useAuthStore
    end
    
    useAuthStore --> LoginPage : user
    deactivate useAuthStore
    
    alt auth.isAdmin is true
        LoginPage -> LoginPage : navigateTo('/admin')
    else auth.isHeadAgent is true
        LoginPage -> LoginPage : navigateTo('/agency')
    else auth.isAgent is true
        LoginPage -> LoginPage : navigateTo('/agent')
    else Default / Client User
        LoginPage -> LoginPage : navigateTo('/')
    end
    
    LoginPage --> Client : dashboard page rendered
end

deactivate LoginPage
@enduml
```

---

## 🛠️ Key Implementation Details

* **Router Mapping**: The frontend Axios client POST request routes directly to the `login()` endpoint defined in `backend/routers/auth.py`.
* **Repository Hook**: `UserRepository.get_by_email` uses the SQLAlchemy session to query the DB directly, returning a Python `models.User` object mapping the `users` table.
* **Encryption Context**: Password validation uses `pwd_context.verify` in the `auth` module, abstracting password hashing (`pbkdf2_sha256`).
* **Active Check**: Even with valid credentials, `is_active` must be `True` to authorize login, preventing disabled agents/staff from accessing the application.
* **Profile Sync**: Upon login, the store calls `fetchUser()` which queries `auth/me` to secure the complete user model (`current_user`) for store context before redirecting.

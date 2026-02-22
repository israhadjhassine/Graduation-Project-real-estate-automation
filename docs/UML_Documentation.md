# Full Project UML Architecture Documentation

This document provides a comprehensive overview of the entire AI-Driven Real Estate Automation Platform architecture. It covers all existing features and planned modules.

---

## 1. Comprehensive Use Case Diagram

This diagram captures every major interaction within the ecosystem, including AI-driven automation and administrative control.

```mermaid
useCaseDiagram
    actor "Visitor" as Visitor
    actor "Sub-Agent" as Agent
    actor "Head Agent" as Manager
    actor "Administrator" as Admin
    actor "System / AI" as AI
    actor "Telegram Bot" as Bot

    package "Property & Search" {
        usecase "Browse & Advanced Filtering" as UC1
        usecase "AI Semantic Search" as UC2
        usecase "View Property & Map" as UC3
        usecase "Save Search & Notify Me" as UC4
        usecase "Manage Favorites" as UC5
    }

    package "Real Estate Operations" {
        usecase "List & Manage Properties" as UC6
        usecase "Manage Agency & Staff" as UC7
        usecase "Schedule & Confirm Visits" as UC8
        usecase "Respond to Inquiries" as UC9
    }

    package "Trust & Moderation" {
        usecase "Verify Listings & Agencies" as UC10
        usecase "Review & Rate Agents" as UC11
        usecase "AI Content Moderation" as UC12
        usecase "View Trust Score Analytics" as UC13
    }

    package "Automation & External" {
        usecase "Telegram Chatbot UI" as UC14
        usecase "Google Calendar Sync" as UC15
        usecase "Auto-generate Descriptions" as UC16
    }

    Visitor --> UC1
    Visitor --> UC2
    Visitor --> UC3
    Visitor --> UC4
    Visitor --> UC5
    Visitor --> UC11
    Visitor --> UC14

    Agent --> UC6
    Agent --> UC8
    Agent --> UC9

    Manager --> UC6
    Manager --> UC7
    Manager --> UC8
    Manager --> UC13

    Admin --> UC10
    Admin --> UC12

    AI --> UC2
    AI --> UC12
    AI --> UC16
    
    Bot --> UC14
    Bot --> UC15
```

---

## 2. Complete Class Diagram (Full System Scope)

This diagram shows all the data entities and how they are interconnected across the entire platform.

```mermaid
classDiagram
    direction TB

    class Agency {
        +BigInt id
        +String name
        +String license_number
        +String logo_url
        +Int trust_score
        +Boolean is_verified
        +Timestamp created_at
    }

    class User {
        +BigInt id
        +String full_name
        +String email
        +String hashed_password
        +String role
        +Boolean is_active
        +BigInt agency_id
    }

    class Property {
        +BigInt id
        +String title
        +String slug
        +Text description
        +Numeric price
        +String property_type
        +String listing_type
        +String status
        +Numeric latitude
        +Numeric longitude
        +Vector description_vector
        +Boolean is_verified
        +BigInt agency_id
        +BigInt owner_id
        +BigInt agent_id
    }

    class PropertyImage {
        +BigInt id
        +String image_url
        +Boolean is_primary
    }

    class Feature {
        +BigInt id
        +String name
    }

    class Appointment {
        +BigInt id
        +Timestamp start_time
        +Timestamp end_time
        +String status
        +String google_event_id
        +BigInt property_id
        +BigInt visitor_id
        +BigInt agent_id
    }

    class Review {
        +BigInt id
        +Int rating
        +Text comment
        +BigInt target_id
        +String target_type
        +BigInt author_id
    }

    class SavedSearch {
        +BigInt id
        +JSON filters
        +Boolean notify_me
        +BigInt user_id
    }

    class ModerationLog {
        +BigInt id
        +String action
        +Text reason
        +BigInt target_id
        +String target_type
        +BigInt admin_id
    }

    %% Relationships
    Agency "1" -- "*" User : has_members
    Agency "1" -- "*" Property : manages
    User "1" -- "*" Property : owns (as Owner)
    User "1" -- "*" Property : assigned (as Agent)
    User "1" -- "*" Appointment : books
    User "1" -- "*" SavedSearch : creates
    User "1" -- "*" Review : writes
    
    Property "1" -- "*" PropertyImage : has_gallery
    Property "1" -- "*" Appointment : has_visits
    Property "*" -- "*" Feature : includes (M2M)
    
    User "*" -- "*" Property : favorites (M2M)
    
    Admin "1" -- "*" ModerationLog : records
```

---

## 3. Core Workflow: Visit Scheduling (Sequence Diagram)

To clarify the "Automation" part of our project, here is how the data flows from a request to a Calendar entry.

```mermaid
sequenceDiagram
    participant V as Visitor (Web/Bot)
    participant F as FastAPI (Backend)
    participant N as n8n (Automation)
    participant G as Google Calendar
    participant A as Sub-Agent

    V->>F: Request Visit (Property ID, Date)
    F->>N: Trigger "Visit Request" Workflow
    N->>G: Check Agent Availability
    G-->>N: Returns Conflicts
    N->>V: Propose available slots
    V->>N: Pick a slot
    N->>G: Create Calendar Event
    G-->>N: Event ID / Confirmation
    N->>F: Update Appointment Status (Confirmed)
    N->>A: Notify Agent (Telegram/Email)
    N->>V: Notify Visitor (Confirmation)
```

---

## 4. Logical Components & Tech Stack

### Frontend (Nuxt.js)
- **Role**: Premium user interface, SEO-optimized landing pages, Map integration.
- **State**: Pinia for user state and favorites.

### Backend (FastAPI)
- **Role**: Core business logic, JWT Security, Semantic search indexing.
- **ORM**: SQLAlchemy with PostgreSQL + pgvector.

### AI Layer (Google Gemini)
- **Role**: Conversion of descriptions to vectors, automated content moderation, conversational RAG.

### Automation Layer (n8n)
- **Role**: "The Glue". Connects the database to external APIs (Telegram, Google Calendar, Email).

# UML Architecture Documentation

This document outlines the system architecture for the AI-Driven Real Estate Automation Platform using UML diagrams.

## 1. Use Case Diagram

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
        usecase "AI Assistant Inquiry (RAG)" as UC4A
    }

    package "Real Estate Operations" {
        usecase "List & Manage Properties (Upload Photos)" as UC6
        usecase "Manage Agency & Staff" as UC7
        usecase "Schedule & Confirm Visits" as UC8
    }

    Visitor --> UC1
    Visitor --> UC2
    Visitor --> UC3
    Visitor --> UC4A

    Agent --> UC8
    Agent --> UC8

    Manager --> UC6
    Manager --> UC7
    Manager --> UC8

    Admin --> UC1
    Admin --> UC3

    AI --> UC2
    
    Bot --> UC8
```

## 2. Class Diagram (Backend Models)

```mermaid
classDiagram
    direction TB
    class Agency {
        +BigInt id
        +String name
        +String license_number
    }

    class User {
        +BigInt id
        +String full_name
        +String email
        +String role
        +Boolean is_active
    }

    class Property {
        +BigInt id
        +String title
        +Numeric price
        +String property_type
        +Vector description_vector
        +BigInt agency_id
        +BigInt head_agent_id
        +BigInt assigned_agent_id
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
        +String status
        +BigInt property_id
        +BigInt visitor_id
        +BigInt agent_id
    }

    class Review {
        +BigInt id
        +Int rating
        +Text comment
    }

    Agency "1" -- "*" User : has_members
    Agency "1" -- "*" Property : manages
    User "1" -- "*" Property : listing_owner (Head Agent)
    User "1" -- "*" Property : listing_agent (Sub-Agent)
    Property "1" -- "*" PropertyImage : has_gallery
    Property "1" -- "*" Appointment : has_visits
    Property "*" -- "*" Feature : includes
    User "1" -- "*" Review : writes
```

## 3. Workflow: Property Upload (Head Agent)
1. **Input**: Head Agent uploads property data and images.
2. **AI Action**: Gemini creates the embedding vector.
3. **Storage**: Data and Images are saved.



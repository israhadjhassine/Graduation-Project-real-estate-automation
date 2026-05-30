# UML Domain Class Diagram — Elite Estate (Conceptual Model)

This is the finalized, academic-grade UML Class Diagram representing the conceptual domain model of the Elite Estate platform.

## 📌 Modeling Decisions & Clarity Notes

* **UML Inheritance vs DB Schema**: While the database stores the user role as a string field (`client`, `agent`, `admin`, `head_agent`) for simplicity, it is modeled here as a class inheritance hierarchy to maintain clean conceptual design and structural clarity.
* **Role-Specific Class Relationships**: Associations are mapped directly to specific user subclasses (`Client`, `Agent`, `HeadAgent`, `Admin`) representing their exact domain roles, rather than using a generic, overly broad `User` class.
* **Association vs DB Schema**: Join tables and foreign key database attributes have been completely removed. Attributes represent strictly domain-level data, while relationships represent structural associations with clear multiplicity.
* **Strict Lifecycle Composition**: Only `PropertyImage` is bound to `Property` using Composition (`*--`), as images cannot exist without their parent property. All other dependencies are modeled as conceptual associations (`-->`).
* **Domain Methods**: Conceptual methods (representing business logic functions) have been added to the classes where they operate.

---

```mermaid
classDiagram
    direction LR

    %% ==========================================
    %% 1. ACCESS CONTROL & USER CLUSTER
    %% ==========================================
    class User {
        +BigInteger id
        +String full_name
        +String email
        +String phone_number
        +String hashed_password
        +Boolean is_active
        +String telegram_chat_id
        +TIMESTAMP created_at
        +register(fullName, email, password) User
        +login(email, password) String
        +updateProfile(fullName, phone) User
    }

    class Admin {
        +createUser(fullName, email, role) User
        +toggleUserStatus(userId) Boolean
        +downloadReport(reportId) File
        +viewSystemStatistics() JSON
    }

    class Client {
        +scheduleVisit(propertyId, visitDate) Visit
        +createTransactionRequest(propertyId, type, price) TransactionRequest
        +linkTelegram(pairingCode) Boolean
    }

    class Agent {
        +manageProperty(propertyId) Property
        +conductVisit(visitId) Boolean
        +handleTransactionRequest(requestId, status) Boolean
        +fileReport(propertyId, type, price) Report
    }

    class HeadAgent {
        +manageAgentTeam(agentId) Boolean
        +viewStatistics() JSON
    }

    class TelegramPairingCode {
        +BigInteger id
        +String code
        +TIMESTAMP expires_at
        +TIMESTAMP created_at
        +verifyCode(code) Boolean
        +checkExpiry() Boolean
    }

    %% User Hierarchy Inheritance
    User <|-- Client
    User <|-- Agent
    User <|-- HeadAgent
    User <|-- Admin

    note for User "Role is stored as enum in DB, but modeled as inheritance for conceptual clarity."

    %% ==========================================
    %% 2. CORE PROPERTY CLUSTER
    %% ==========================================
    class Property {
        +BigInteger id
        +String title
        +String slug
        +Text description
        +String property_type
        +String listing_type
        +String status
        +Numeric price
        +String currency
        +Numeric area
        +Integer bedrooms
        +Integer bathrooms
        +Integer kitchens
        +Integer living_rooms
        +Integer floors
        +Integer floor_number
        +String country
        +String state
        +String city
        +String neighborhood
        +Text address
        +String postal_code
        +Numeric latitude
        +Numeric longitude
        +Boolean is_featured
        +TIMESTAMP published_at
        +TIMESTAMP rent_start_date
        +TIMESTAMP rent_end_date
        +TIMESTAMP created_at
        +TIMESTAMP updated_at
        +Vector description_vector
        +publish() Boolean
        +updateDetails(title, price, area) Property
        +archive() Boolean
        +searchSemantic(queryText) List~Property~
        +addFeature(featureId) Boolean
        +removeFeature(featureId) Boolean
    }

    class PropertyImage {
        +BigInteger id
        +String image_url
        +String file_id
        +Boolean is_primary
        +TIMESTAMP created_at
        +setPrimary() Boolean
        +deleteImage() Boolean
    }

    class Feature {
        +BigInteger id
        +String name
        +createFeature(name) Feature
    }

    %% Property Enums
    class PropertyStatus {
        <<enumeration>>
        available
        pending_sold
        pending_rent
        sold
        rented
    }

    class ListingType {
        <<enumeration>>
        sale
        rent
    }

    class PropertyType {
        <<enumeration>>
        apartment
        house
        villa
        studio
        office
    }

    %% ==========================================
    %% 3. TRANSACTION & SCHEDULING CLUSTER
    %% ==========================================
    class Visit {
        +BigInteger id
        +TIMESTAMP visit_date
        +String status
        +Boolean reminder_sent
        +String telegram_chat_id
        +TIMESTAMP created_at
        +TIMESTAMP updated_at
        +reschedule(newDate) Boolean
        +confirmVisit() Boolean
        +cancelVisit() Boolean
        +sendReminder() Boolean
    }

    class Report {
        +BigInteger id
        +String transaction_type
        +Numeric price_at_time
        +TIMESTAMP created_at
        +generatePDF() File
        +download() File
    }

    class TransactionRequest {
        +BigInteger id
        +String type
        +String status
        +Numeric price
        +TIMESTAMP rent_start_date
        +TIMESTAMP rent_end_date
        +TIMESTAMP created_at
        +TIMESTAMP updated_at
        +approve() Boolean
        +reject() Boolean
        +cancel() Boolean
    }

    %% Scheduling Enums
    class VisitStatus {
        <<enumeration>>
        scheduled
        finished
        cancelled
    }

    class TransactionStatus {
        <<enumeration>>
        pending
        approved
        rejected
    }

    class TransactionType {
        <<enumeration>>
        Sale
        Rent
    }

    %% ==========================================
    %% RELATIONSHIPS & ASSOCIATIONS
    %% ==========================================

    %% Role-Specific User Associations
    Client --> Property : owns
    Agent --> Property : manages

    Client --> Visit : schedules
    Agent --> Visit : conducts

    Client --> TransactionRequest : creates
    Agent --> TransactionRequest : handles

    Agent --> Report : files
    Client --> Report : participates

    User --> TelegramPairingCode : generates
    Agent --> HeadAgent : reports to

    %% Admin Management & Oversight
    Admin --> User : manages
    Admin --> Report : audits

    %% Property Associations & Strict Composition
    Property "1" *-- "*" PropertyImage : contains
    Property --> Visit : has visits
    Property --> Report : generates reports
    Property --> TransactionRequest : triggers

    %% Many-To-Many Feature Association (Named property_features)
    Property "*" -- "*" Feature : property_features

    %% Enum Dependency Links
    Property --> PropertyStatus
    Property --> ListingType
    Property --> PropertyType

    Visit --> VisitStatus

    TransactionRequest --> TransactionStatus
    TransactionRequest --> TransactionType
```

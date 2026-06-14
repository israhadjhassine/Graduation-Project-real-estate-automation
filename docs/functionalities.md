# Elite Estate - Functional Specifications by Role

This document details the functionalities available to each user role in the Elite Estate system.

---

## 1. Visitor (Anonymous/Public)
The public interface for anyone browsing the platform.
*   **Property Browsing**: View all available properties.
*   **Basic Filtered Search**: Filter listings by location, price range, property type, and specific features/amenities.
*   **Map Integration**: View property locations on the interactive Leaflet map.
*   **Registration**: Create a new account to unlock personalized AI features and scheduling services.

---

## 2. Client (Registered User)
An authenticated user who has joined the Elite Estate platform.
*   **Profile Management**: Update personal info (name, phone, email) and change password securely.
*   **Smart AI Search**: Search for properties using natural language (semantic search powered by Ollama embeddings).
*   **Visit Booking**: Schedule visit appointments for specific properties with automatic sub-agent availability checks.
*   **Telegram Bot AI Assistant (RAG)**: Interact with the AI bot to search properties, ask specific questions about any property (e.g., "Is the neighborhood quiet?") with context-grounded responses, schedule visits, and receive automated reminders (leveraging persistent PostgreSQL chat memory).
*   **Property Notifications**: If a client lists a property or is buying/renting one:
    *   View status updates for their property.
    *   Receive automated email reports when their property is sold or rented.

---

## 3. Sub-Agent (Standard Agent)
The field agents responsible for showing properties and initiating transactions.
*   **Property Assignment**: Receive and view properties assigned to them by a Head Agent.
*   **Visit Management**:
    *   Receive and manage visit requests for their assigned properties.
    *   View scheduled visits on their dashboard's timeline.
    *   Receive Telegram notifications for new visits.
*   **Transaction Workflow**:
    *   Update property status to "Pending Sold" or "Pending Rent".
    *   **Request Approval**: Submit a transaction request to the Head Agent when a deal is ready.
*   **AI Tools**: Access the same RAG search and property assistant tools to help answer client questions.

---

## 4. Head Agent (Agency Manager)
The manager of an agency branch or a specific team.
*   **Team Management**:
    *   Create accounts for Sub-Agents.
    *   Monitor Sub-Agent activity and toggle their account status (Active/Inactive).
*   **Inventory Control**:
    *   **Full CRUD**: Create, Update, and Delete property listings.
    *   **Image Management**: Upload and manage high-quality property photos via ImageKit.
    *   **AI Content**: Automatically generate AI embeddings for property descriptions during creation/update.
*   **Resource Allocation**: Assign specific properties to Sub-Agents.
*   **Financial Oversight**:
    *   **Approval System**: Approve or reject transaction requests submitted by Sub-Agents.
    *   **Finalization**: Set properties to "Sold" or "Rented", which automatically generates reports and closes the listing.
*   **Reporting**: View agency-wide statistics and performance reports.

---

## 5. Admin (System Administrator)
The top-level user with full system access.
*   **Global Oversight**: Access all properties, users, and reports across the entire platform.
*   **Advanced User Management**:
    *   Create and manage **Head Agent** accounts.
    *   Manage any staff account across all agencies.
*   **Data Integrity**:
    *   Manually override or fix property data.
    *   Directly finalize any transaction.
*   **System Configuration**: Create and manage the global list of **Amenities/Features** (e.g., adding "Solar Panels" as a selectable tag).
*   **Analytics**: Access comprehensive system-wide statistics.

# Elite Estate - Functional Specifications by Role

This document details the functionalities available to each user role in the Elite Estate system.

---

## 1. Visitor (Anonymous/Public)
The public interface for anyone browsing the platform.
*   **Property Browsing**: View all properties marked as "available".
*   **Advanced Search**: 
    *   **Semantic Search**: Search for properties using natural language (powered by AI embeddings).
    *   **Filtered Search**: Filter by location, price, property type, and specific amenities.
*   **AI Property Assistant (RAG)**: Ask specific questions about any property (e.g., "Is the neighborhood quiet?") and get answers based on the property's description.
*   **Map Integration**: View property locations on Google Maps.
*   **Registration**: Create a new account to become a Client.

---

## 2. Client (Registered User)
A standard user who interacts with the agency.
*   **Profile Management**: Update personal info (name, phone, email) and change password.
*   **Property Ownership**: If a client owns a property listed with the agency:
    *   View status updates for their property.
    *   Receive automated email reports when their property is sold or rented.
*   **Booking History**: (Planned/Contextual) View history of visits or transaction requests.

---

## 3. Sub-Agent (Standard Agent)
The field agents responsible for showing properties and initiating transactions.
*   **Property Assignment**: Receive and view properties assigned to them by a Head Agent.
*   **Visit Management**:
    *   Receive visit requests for their assigned properties.
    *   Sync visits with their **Google Calendar** automatically.
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

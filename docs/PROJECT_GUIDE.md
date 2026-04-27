# Elite Estate: Project Documentation & Technical Overview

## 1. Project Overview
**Elite Estate** is an AI-driven real estate automation platform designed to modernize the property management lifecycle. It bridges the gap between traditional real estate operations and modern AI-powered automation, providing a seamless experience for visitors, agents, and administrators.

The core value proposition lies in its integration of **Semantic Search**, **Generative AI Assistants (RAG)**, and **Telegram-based Automation**, ensuring that property discovery and visit scheduling are efficient, data-driven, and highly automated.

---

## 2. User Roles & Functionalities

The platform implements a robust **Role-Based Access Control (RBAC)** system with four distinct roles:

### 👤 Visitor (Public User)
*   **Property Discovery**: Browse property listings with high-quality galleries.
*   **AI Semantic Search**: Search for properties using natural language (e.g., "cozy beachfront villa for a large family").
*   **Property Q&A**: Interact with a property-specific AI assistant to ask detailed questions (e.g., "Is there a lot of sunlight in the morning?").
*   **Visit Booking**: Request visit appointments directly through the Telegram bot.
*   **Interactive Maps**: View exact property locations via integrated Leaflet maps.

### 🧑‍💼 Sub-Agent
*   **Visit Management**: View and manage assigned visit requests.
*   **Inquiry Tracking**: Track client leads and update the status of property inquiries.
*   **Calendar Sync**: View scheduled visits that are automatically synchronized with Google Calendar.

### 🏅 Head Agent (Manager)
*   **Listing Management**: Full CRUD (Create, Read, Update, Delete) capabilities for properties.
*   **Media Management**: Upload and manage high-resolution property images via ImageKit CDN.
*   **Agent Supervision**: Manage and assign properties/leads to sub-agents.
*   **Transaction Approval**: Review and approve property sales or rentals initiated by sub-agents.

### 🔑 Administrator
*   **System Overlook**: Full access to all platform data and user accounts.
*   **Analytics Dashboard**: View platform-wide KPIs, including visit trends, property performance, and agent productivity charts.
*   **User Management**: Handle account creation, role assignments, and hierarchy management.

---

## 3. Core Features & Functionalities

### 🔍 AI Semantic Search (Vector-Based)
Traditional keyword search is replaced/augmented by **pgvector**. 
- **How it works**: Property descriptions are converted into 768-dimensional vectors using the `nomic-embed-text` model via Ollama.
- **Benefit**: Users can find properties based on "intent" and "vibe" rather than just matching words.

### 🤖 RAG Property Assistant
Each property page features a **Retrieval-Augmented Generation (RAG)** chatbot.
- **Grounding**: The AI (Gemini 1.5 Pro) is strictly constrained to the property's specific data (amenities, description, location) to prevent hallucinations.
- **Interactivity**: Provides instant answers to granular questions that might not be prominently listed in the UI.

### 📱 Smart Telegram Agent
A sophisticated n8n-powered Telegram bot that acts as a 24/7 virtual assistant.
- **Capabilities**: Searching properties, fetching details, scheduling visits, and checking agent availability.
- **Memory**: Features persistent PostgreSQL chat memory, allowing it to remember past interactions with the same user.

### 🗓️ Automated Scheduling & Reminders
- **Google Calendar Integration**: Visits booked on the platform or via Telegram are instantly pushed to the assigned agent's Google Calendar.
- **Meeting Reminders**: An automated n8n workflow polls for upcoming visits and sends automated Telegram notifications to clients 24 hours (or 1 hour) before the meeting.

---

## 4. Key Data Flows

### A. Property Listing & Embedding Flow
1.  **Input**: Head Agent submits property details + images.
2.  **Storage**: Images are cached and optimized via **ImageKit**.
3.  **Embedding**: Backend sends the description to **Ollama**; receiving a vector.
4.  **Database**: PostgeSQL stores relational data while **pgvector** stores the AI embedding.
5.  **Output**: Listing becomes immediately available for both keyword and semantic search.

### B. Intelligent Search Workflow
1.  **Query**: User enters "Modern apartment with a pool near Sfax".
2.  **Vectorization**: The query is converted into a vector in real-time.
3.  **Similarity Search**: PostgreSQL performs a cosine similarity search against all stored property vectors.
4.  **Result**: The user receives a list of properties ranked by how well they match the *meaning* of the search.

### C. Automated Visit Booking Flow
1.  **Trigger**: User (Visitor) books a visit via Web or Telegram.
2.  **Validation**: Backend checks agent availability.
3.  **Creation**: A visit record is created in PostgreSQL.
4.  **Automation (n8n)**: 
    -   Triggers a Google Calendar event creation for the agent.
    -   Stores the client's Telegram ID for future reminders.
5.  **Reminder**: An hourly cron job sends a Telegram push notification to the client before the visit.

---

## 5. Technology Stack Summary

| Layer | Technology |
| :--- | :--- |
| **Frontend** | Nuxt 3 (Vue.js), TailwindCSS, Pinia |
| **Backend** | FastAPI (Python), SQLAlchemy, Pydantic |
| **Database** | PostgreSQL + pgvector |
| **AI Models** | Google Gemini 1.5 (Flash/Pro), Ollama (nomic-embed-text) |
| **Automation** | n8n (Self-hosted), Telegram Bot API |
| **Infrastructure** | Docker, Docker Compose, ngrok (sidecar) |
| **Storage** | ImageKit.io (Media CDN) |

---

> [!IMPORTANT]
> **Elite Estate** is built using the **Service-Router pattern**, ensuring that the AI, Database, and Automation layers are decoupled and independently scalable.

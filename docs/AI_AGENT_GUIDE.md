# AI Agent Handover & Technical Blueprint

**Project Name**: AI-Driven Real Estate Automation Platform  
**Current State**: Foundation and Core Security Complete  
**Last Update**: 2026-02-22  

---

## 🤖 Instructions for the Joining AI Agent

Hello fellow Agent! You are assisting the partner in developing this Real Estate Platform. To stay on track and ensure consistency, please follow these guidelines and technical constraints.

### 1. The Core Infrastructure
- **Frontend**: Nuxt.js 4 (Vue 3) using TailwindCSS and Pinia.
- **Backend**: FastAPI (Python 3.11+) with SQLAlchemy.
- **Database**: PostgreSQL with the `pgvector` extension for AI semantic search.
- **Automation**: n8n (Dockerized) for Telegram, Google Calendar, and Email flows.
- **AI**: Google Gemini API (`text-embedding-004`) for vectorization and RAG.

### 2. Implementation Progress (The "Truth")
Refer to the following files in the repository for the most up-to-date status:
- `task.md`: Current checklist and implementation status.
- `docs/UML_Documentation.md`: Detailed Use Case and Class Diagrams.
- `backend/models.py`: Current database schema.
- `backend/auth.py`: JWT-based Authentication and RBAC implementation.

### 3. Strict Coding Rules (Shared Rules)
1. **Explain the Workflow**: Before giving code, explain the Frontend → Backend → Database data flow.
2. **Security**: Never push `.env` files. Always use the variables defined in `docker-compose.yml`.
3. **Database**: Use `pgvector` for description columns. Do not use external vector DBs like Pinecone.
4. **Consistency**: Use the existing `database.py` session management and Pydantic schemas in `schemas.py`.

### 4. Technical Context for next steps
- **Authentication**: JWT is implemented using `HS256`. Token expiry is set to 60 mins.
- **RBAC**: A `RoleChecker` dependency exists in `auth.py`. Available roles: `visitor`, `agent`, `head_agent`, `admin`.
- **Seeding**: A `backend/seed.py` exists to populate the DB for development. Run it via:  
  `docker exec -it FastAPI_backend python seed.py`

### 5. Immediate Roadmap
1. **Property Management**: Implementation of full CRUD for listings (Multi-image upload, feature tags).
2. **Agency Logic**: Restricting property visibility based on `agency_id`.
3. **AI Search**: Connecting the Gemini embedding logic to the `description_vector` in PostgreSQL.

---

## 🎯 Core User Functionalities

### 1. Visitor (Client)
- **Advanced Search**: Filter by price, location, bedrooms, property type (sale/rent).
- **AI Semantic Search**: Natural language queries (e.g., "Cozy quiet house near the beach").
- **Interactive Map**: Visualize property locations using Leaflet.
- **Favorites**: Heart/Save properties for later (Personalized dashboard).
- **Saved Searches**: Get notified when new properties match specific criteria.
- **Telegram Bot**: Search properties and inquire via chat.

### 2. Sub-Agent
- **Listing Management**: CRUD properties (Title, price, detailed specs).
- **Image Gallery**: Upload and manage multiple photos (Set primary image).
- **Amenities Logic**: Tag properties with features (Pool, Garden, WIFI).
- **Calendar Sync**: View and manage visit appointments synced with Google Calendar.
- **Inquiry Management**: Respond to leads from Telegram/Web.

### 3. Head Agent (Manager)
- **Staff Control**: Recruit and manage Sub-Agents for their Agency.
- **Performance View**: Monitor total listings and visit counts for the agency.
- **Trust Score**: Responsible for maintaining the agency's verification status.

### 4. Administrator
- **Platform Moderation**: Use the `ModerationLog` to verify/block suspicious listings.
- **User Management**: Approve/Revoke access for Head Agents and Agencies.
- **Trust Analytics**: Monitor platform-wide safety trends.

---

## 🔄 Core System Workflows

### ⚡ Workflow A: AI Semantic Search
1. **Request**: User enters "Modern villa for a large family" on Nuxt frontend.
2. **FastAPI**: Sends text to **Google Gemini API** (`text-embedding-004`).
3. **PostgreSQL**: Performs a **Cosine Similarity** search on the `description_vector` column using `pgvector`.
4. **Result**: Returns top matches based on "concept" rather than just keywords.

### ⚡ Workflow B: Visit Scheduling (The "n8n Glue")
1. **Trigger**: User clicks "Schedule Visit" on a Property page or Telegram.
2. **n8n Workflow**:
   - Checks the assigned Agent's **Google Calendar** for free slots.
   - Proposes slots to the User.
   - User picks a time.
3. **Action**: n8n creates the Calendar event AND sends a **Telegram Notification** to the Agent.
4. **Update**: FastAPI updates the appointment status in the database to `confirmed`.

### ⚡ Workflow C: Lead Acquisition via Telegram
1. **Bot Interaction**: User finds a property on the Telegram Bot.
2. **Webhook**: Telegram sends data to **n8n**.
3. **Capture**: n8n stores the lead details in the DB and notifies the listing Agent.

### ⚡ Workflow D: Trust & Moderation Audit
1. **AI Flag**: Gemini scans a newly uploaded description.
2. **Risk Check**: If spam/toxicity is high, the property is set to `pending`.
3. **Logging**: A record is created in `ModerationLog`.
4. **Admin Review**: Admin sees the flag in the dashboard and decides to Approve/Reject.

---

## 📅 Full Project Checklist (Roadmap)

Please keep this checklist updated as you work through features with your partner.

### 1. Project Initialization
- [x] Analyze requirements and documentation
- [x] Explore existing codebase
- [x] Create implementation plan
- [x] Update `docker-compose.yml` to match documentation (FastAPI, Nuxt.js)
- [x] Configure Environment & OAuth (Google Console)

### 2. Backend Development (FastAPI)
- [x] Initialize FastAPI project
- [x] Set up Database models (PostgreSQL + pgvector)
- [x] Database Seeding (Initial Users & Properties)
- [/] Implement JWT Authentication and RBAC
- [ ] Create core endpoints (Properties, Agencies, Users, Appointments)
- [ ] Implement advanced search and filtering system
- [ ] Implement user features (favorites, saved searches)

### 3. Frontend Development (Nuxt.js)
- [x] Initialize Nuxt.js project with TailwindCSS
- [ ] Implement Premium UI Design System (Hero section, typography, spacing)
- [ ] Build Advanced Search & Filtering UI
- [ ] Build Property Detail Pages (Gallery, amenities, map integration)
- [ ] Implement Map-based browsing
- [ ] Build Dashboards and User Account features

### 4. Automation & Orchestration (n8n)
- [ ] Set up n8n workflows
- [ ] Integrate Telegram Bot
- [ ] Implement Google Calendar sync logic (OAuth2 flow)

### 5. AI Service Integration
- [ ] Implement Semantic Search (pgvector + Google Gemini Embeddings)
- [ ] Set up RAG for property inquiries (Gemini Pro)

### 6. Verification & Deployment
- [ ] End-to-end testing
- [x] Create UML Documentation (Use Case, Class Diagrams)
- [x] Create Collaboration & Git Guide
- [x] Create AI Agent Handover Guide (for partner's agent)
- [ ] Documentation update

---

**Signed**: *The Master Agent (Antigravity)*  
*Let's build something amazing together!*

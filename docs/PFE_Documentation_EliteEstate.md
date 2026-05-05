# PFE Technical Documentation
## AI-Driven Real Estate Automation Platform — *Elite Estate*

**Project Type**: End-of-Study Project (Projet de Fin d'Études — PFE)  
**Institution**: ISET  
**Platform Name**: Elite Estate  
**Academic Year**: 2025–2026  
**Language**: English  

---

## Table of Contents

1. [Project Overview & Context](#1-project-overview--context)
2. [Problem Statement & Objectives](#2-problem-statement--objectives)
3. [Research Methodology](#3-research-methodology)
4. [Technology Stack — State of the Art & Justification](#4-technology-stack--state-of-the-art--justification)
5. [System Architecture](#5-system-architecture)
6. [Technical Achievements](#6-technical-achievements)
   - 6.1 [Backend — FastAPI Service Layer](#61-backend--fastapi-service-layer)
   - 6.2 [Database Design — PostgreSQL + pgvector](#62-database-design--postgresql--pgvector)
   - 6.3 [AI & Semantic Search Pipeline](#63-ai--semantic-search-pipeline)
   - 6.4 [Frontend — Nuxt 3 Web Application](#64-frontend--nuxt-3-web-application)
   - 6.5 [Automation Layer — n8n Workflows](#65-automation-layer--n8n-workflows)
   - 6.6 [Cloud Image Management — ImageKit](#66-cloud-image-management--imagekit)
   - 6.7 [DevOps — Docker Containerization](#67-devops--docker-containerization)
7. [Problems Encountered & Solutions Applied](#7-problems-encountered--solutions-applied)
8. [Results & Validation](#8-results--validation)
9. [UML Documentation](#9-uml-documentation)
10. [Conclusions & Future Prospects](#10-conclusions--future-prospects)

---

## 1. Project Overview & Context

**Elite Estate** is a full-stack, AI-powered real estate management and automation platform developed as an end-of-study project (PFE). The project was built collaboratively by a two-person team, with each member owning a distinct technical domain:

| Team Member | Domain |
|---|---|
| Member A | Full-stack platform engineering (Backend, Frontend, Database, DevOps) |
| Member B | AI automation and workflow engineering (n8n, Telegram, Google Calendar, RAG) |

The platform is designed to digitize and automate the full lifecycle of a real estate agency: from property listing and client discovery, through visit scheduling, to the final transaction report generation. It targets the Tunisian real estate market and is currency-aware (TND).

> [!NOTE]
> This project goes significantly beyond a standard ISET PFE scope. It incorporates enterprise-grade patterns including AI/ML vector embeddings, OAuth2, multi-container Docker orchestration, and real-time webhook automation — technologies more commonly seen in engineering school final-year projects.

---

## 2. Problem Statement & Objectives

### 2.1 The Problem

Traditional real estate agencies in Tunisia operate with fragmented, manual processes:
- Property listings exist on disconnected spreadsheets or simple websites with no intelligent search.
- Client inquiries arrive via phone calls, with no structured tracking or response system.
- Visit scheduling is managed manually, leading to missed appointments and poor client experience.
- Agents have no unified dashboard to track their assigned properties, pending visits, or sales status.
- Administrators have no visibility into platform-wide performance or transaction history.

### 2.2 Project Objectives

The project was designed to solve each of these problems through a single, unified platform:

| # | Objective | Solution Built |
|---|---|---|
| 1 | Intelligent property search beyond keyword matching | AI Semantic Search (pgvector + Gemini Embeddings) |
| 2 | Structured client inquiry and visit request system | Visit management module with RBAC |
| 3 | Automated appointment reminders for clients and agents | n8n Meeting Reminder Workflow |
| 4 | Real-time client engagement via messaging apps | Telegram bot with AI agent (RAG) |
| 5 | Calendar synchronization for agent availability | Google Calendar OAuth2 integration via n8n |
| 6 | Transaction tracking and report generation | Automated email reports and approval workflow |
| 7 | Role-based multi-stakeholder platform | 4-role RBAC: Admin, Head Agent, Sub-Agent, Visitor |

---

## 3. Research Methodology

The project followed an **Agile/Scrum-inspired** iterative development methodology, adapted for a two-person academic team:

### 3.1 Development Phases

```
Phase 1: Research & Architecture Design
  → Technology comparison, stack selection, UML modeling

Phase 2: Core Infrastructure
  → Docker Compose setup, Database schema, Authentication

Phase 3: Backend API Development
  → FastAPI routers, RBAC, property CRUD, semantic search

Phase 4: Frontend Development
  → Nuxt 3 UI, role-based dashboards, component library

Phase 5: AI & Automation Integration
  → Gemini embeddings, RAG pipeline, n8n workflows

Phase 6: Testing & Documentation
  → End-to-end testing, UML finalization, PFE report
```

### 3.2 Collaboration Model

The team used **Git and GitHub** as the primary collaboration tool:
- Feature branches were created for each major domain (`feature/auth`, `feature/n8n-telegram`).
- A shared `.env.example` file was maintained to synchronize environment configuration without exposing secrets.
- A dedicated `docs/` folder was created in the repository to centralize all technical guides, including architecture overviews, UML diagrams, troubleshooting logs, and AI agent handover guides.

---

## 4. Technology Stack — State of the Art & Justification

### 4.1 Backend Framework: FastAPI (Python)

**Chosen over**: Django REST Framework, Flask, Node.js/Express.

| Criterion | FastAPI | Django REST | Flask |
|---|---|---|---|
| Performance | ⭐⭐⭐⭐⭐ (async, ASGI) | ⭐⭐⭐ | ⭐⭐⭐ |
| Auto-generated API docs | ✅ (Swagger/OpenAPI) | ⚠️ (requires drf-yasg) | ❌ |
| Type safety (Pydantic) | ✅ Native | ⚠️ External | ❌ |
| AI/ML ecosystem (Python) | ✅ | ✅ | ✅ |
| Learning curve | Low | High (heavy) | Low |

**Justification**: FastAPI's native Pydantic integration enables strict request/response validation with minimal boilerplate. Its async-first design is essential for handling concurrent I/O operations (image uploads, AI API calls, email sending) without blocking the main thread.

### 4.2 Database: PostgreSQL + pgvector

**Chosen over**: MySQL, MongoDB, Pinecone (standalone vector DB).

The critical decision was to use **pgvector** — an open-source PostgreSQL extension that adds vector storage and similarity search directly into the relational database. This eliminates the need for a separate vector database service, reducing infrastructure complexity and cost.

- **`pgvector`** stores AI embedding vectors alongside relational property data.
- Cosine similarity search (`<=>` operator) is used to find semantically similar properties.
- The embedding dimension is **768**, matching the `nomic-embed-text` model used via Ollama.

### 4.3 Frontend Framework: Nuxt 3 (Vue.js)

**Chosen over**: Next.js (React), plain Vue.js SPA, Angular.

- **Server-Side Rendering (SSR)** is critical for a real estate platform, as SEO drives organic traffic to property listings.
- **File-system routing** in Nuxt 3 maps directly to the application's URL structure.
- **Pinia** state management provides a clean, type-safe global store for authentication state.
- **TailwindCSS** enables rapid development of a premium, responsive UI system.

### 4.4 Automation Engine: n8n (Self-Hosted)

**Chosen over**: Zapier, Make (Integromat), custom Python scripts.

n8n was selected because:
1. It is **self-hosted** — all workflow data stays within the project's Docker network without any third-party SaaS dependency.
2. It provides a **low-code visual editor** for building complex, multi-step automation flows with conditional logic.
3. It natively supports **webhook triggers**, essential for the Telegram bot integration.
4. It has first-class support for **Google Calendar OAuth2** and **AI Agent nodes** with tool-use capabilities.

### 4.5 AI Models: OpenRouter (Gemini 2.0 Flash) + Ollama (nomic-embed-text)

| Model | Purpose | Provider |
|---|---|---|
| `nomic-embed-text` (768-dim) | Generating vector embeddings for property descriptions | Ollama (local) |
| `gemini-1.5-pro` | RAG-based property Q&A assistant (generative) | OpenRouter |
| `gemini-2.0-flash` (n8n agent) | Intelligent Telegram bot responses with tool use | OpenRouter (via n8n) |

The dual-model strategy separates embedding generation (local, fast, no cost) from generation (cloud, powerful, context-aware). The switch to OpenRouter ensures high availability and access to the latest frontier models like Gemini 2.0.

---

## 5. System Architecture

The platform follows a **Containerized Micro-Architecture** pattern. All services run as isolated Docker containers connected via a single private Docker network (`real_estate_network`).

```
┌────────────────────────────────────────────────────────────┐
│                    Docker Network (Bridge)                  │
│                                                            │
│  ┌──────────┐    ┌──────────────┐    ┌─────────────────┐  │
│  │  Nuxt 3  │───▶│   FastAPI    │───▶│  PostgreSQL      │  │
│  │ Frontend │    │   Backend    │    │  + pgvector      │  │
│  │ :3000    │    │   :8000      │    │  :5432           │  │
│  └──────────┘    └──────┬───────┘    └─────────────────┘  │
│                         │                                   │
│                  ┌──────▼───────┐    ┌─────────────────┐  │
│                  │ External APIs│    │  n8n Automation  │  │
│                  │ - Gemini API │    │  :5678           │  │
│                  │ - ImageKit   │    └────────┬────────┘   │
│                  │ - SMTP       │             │            │
│                  └──────────────┘    ┌────────▼────────┐   │
│                                      │  ngrok Tunnel   │   │
│                                      │  (HTTPS Bridge) │   │
│                                      └────────┬────────┘   │
└───────────────────────────────────────────────┼────────────┘
                                                │
                               ┌────────────────▼──────────────────┐
                               │         External Services          │
                               │  - Telegram Bot API               │
                               │  - Google Calendar API            │
                               │  - Google OAuth2                  │
                               └───────────────────────────────────┘
```

### Service Manifest

| Service | Container Name | Technology | Exposed Port |
|---|---|---|---|
| `frontend` | `nuxt_ui` | Nuxt 3 / Vue 3 / TypeScript | 3000 |
| `backend` | `FastAPI_backend` | FastAPI / Python 3.11 | 8000 |
| `postgres` | `real_estate_db` | PostgreSQL 16 + pgvector | 5432 |
| `n8n` | `n8n_automation` | n8n self-hosted | 5678 |
| `ngrok` | *(sidecar)* | ngrok tunnel | 4040 |

---

## 6. Technical Achievements

### 6.1 Backend — FastAPI Service Layer

The backend was built using a **Service-Router pattern** — a clean separation of concerns where:
- **Routers** (`/routers/`) handle HTTP request/response lifecycle, input validation (via Pydantic schemas), and authentication.
- **Services** (`/services/`) encapsulate all third-party integrations (AI, email, cloud storage), making them independently testable.

#### 6.1.1 Authentication & Security (RBAC)

A complete JWT-based authentication system was implemented from scratch:

- **Password Hashing**: `pbkdf2_sha256` via `passlib` — chosen over `bcrypt` for better Docker container compatibility.
- **Token Standard**: `HS256`-signed JSON Web Tokens (JWT) with a 60-minute expiry.
- **Role-Based Access Control**: A reusable `RoleChecker` dependency class enforces access at the route level.

```python
# Usage example — only head_agent and admin can create properties
@router.post("/properties", ...)
def create_property(
    current_user: models.User = Depends(auth.RoleChecker(["head_agent", "admin"]))
):
    ...
```

The four defined roles and their permissions:

| Role | Permissions |
|---|---|
| `visitor` | Browse properties, use AI search, book visits |
| `sub_agent` | Manage assigned visits and inquiries |
| `head_agent` | Create/edit listings, manage sub-agents, approve transactions |
| `admin` | Full platform access, user management, statistics |

#### 6.1.2 REST API Endpoints

The API is organized into 5 domain-specific routers:

| Router | File | Key Endpoints |
|---|---|---|
| Auth | `routers/auth.py` | `POST /auth/login`, `POST /auth/register`, `GET /auth/me` |
| Properties | `routers/properties.py` | Full CRUD, image upload, semantic search, RAG Q&A |
| Visits | `routers/visits.py` | Schedule, confirm, cancel, reminder system |
| Reports | `routers/reports.py` | Transaction approval, PDF/plain-text report generation |
| Statistics | `routers/statistics.py` | Platform-wide KPIs for admin and head-agent dashboards |

#### 6.1.3 Transaction Workflow & Email Automation

When a sub-agent marks a property as `pending_sold` or `pending_rent`, the backend automatically:
1. Records the buyer's identity and (for rent) the rental period dates.
2. Dispatches an asynchronous background task (using FastAPI's `BackgroundTasks`) to send a formatted HTML email to the Head Agent requesting approval.
3. The Head Agent approves or rejects through the platform, triggering a second email notification to the sub-agent.

This is a fully integrated, non-blocking transactional email workflow.

---

### 6.2 Database Design — PostgreSQL + pgvector

#### Core Entity-Relationship Summary

The database schema contains **6 primary tables** and **1 association table**:

| Table | Description |
|---|---|
| `users` | All platform users, with `role`, `manager_id` (self-referential FK for hierarchy), and `google_calendar_id` |
| `properties` | Full property data: type, price, location, dimensions, status, and `description_vector` (Vector 768) |
| `property_images` | One-to-many property gallery, stored as absolute ImageKit CDN URLs |
| `features` | Amenity tags (Pool, Elevator, Garden, etc.) |
| `property_features` | Many-to-many join table between properties and features |
| `visits` | Appointments: property, client, agent, date/time, status, Telegram chat ID |

#### Key Design Decisions

1. **Self-Referential User Hierarchy**: The `manager_id` column in `users` creates an organizational tree. Sub-Agents have a `head_agent` as their manager, enabling the platform to enforce agency-scoped data filtering without a separate `agencies` table.

2. **Vector Embedding Column**: The `description_vector` column (type `Vector(768)`) stores the AI-generated semantic embedding of each property's description. This column is the foundation of the platform's intelligent search capability.

3. **Telegram Bridge on Visits**: The `telegram_chat_id` column on the `visits` table stores the Telegram user ID of the client. This allows the n8n reminder workflow to send a personalized Telegram message directly to the client before their scheduled visit.

---

### 6.3 AI & Semantic Search Pipeline

This is one of the most technically significant components of the project. Two distinct AI features were built:

#### 6.3.1 AI Semantic Search (Vector Similarity)

**The Problem**: Keyword search fails when a user searches for "cozy home near the sea" but the listing uses "peaceful villa with ocean views." The words don't match, but the concepts do.

**The Solution**: Vector similarity search powered by pgvector.

**The Workflow**:
```
1. [Property Created]
   → Backend calls Ollama (nomic-embed-text model)
   → Receives a 768-dimensional float vector representing the description's "meaning"
   → Stores vector in property's `description_vector` column (pgvector)

2. [User Searches]
   → User query is embedded into the same 768-dimensional space
   → PostgreSQL performs cosine similarity search:
        SELECT * FROM properties
        ORDER BY description_vector <=> query_vector
        LIMIT 10;
   → Returns the most semantically similar properties
```

This means a search for "family home with space for children" can return listings mentioning "large garden villa" even with zero keyword overlap.

#### 6.3.2 AI Property Assistant (RAG Q&A)

**The Problem**: Visitors have specific questions about individual properties ("Is there parking?", "How sunny is this apartment?") that are not always explicitly in the listing.

**The Solution**: A Retrieval-Augmented Generation (RAG) chatbot, scoped to a single property.

**The Workflow**:
```
1. Visitor asks: "Does this property have good sun exposure?"

2. FastAPI retrieves from PostgreSQL:
   - Property title, description, amenity list, location, dimensions

3. Constructs a structured context string and sends to Gemini 1.5 Pro:
   "You are a real estate assistant. Answer ONLY from this context:
    Title: Sunny Villa in Tunis...
    Amenities: Pool, Garden...
    Question: Does this property have good sun exposure?"

4. Gemini generates a grounded, context-specific answer.
   → Returned to user in real time.
```

The critical RAG constraint — "answer *only* from this context" — prevents the AI from hallucinating facts about a property.

---

### 6.4 Frontend — Nuxt 3 Web Application

The frontend was built as a multi-role, premium-design web application using **Nuxt 3** with **TypeScript** and **TailwindCSS**.

#### 6.4.1 Page Architecture

```
pages/
├── index.vue               → Public homepage with hero section & featured properties
├── properties/
│   ├── index.vue           → Advanced search + semantic search with filters
│   └── [id].vue            → Property detail: gallery, map (Leaflet), AI assistant
├── dashboard/
│   └── profile.vue         → Unified profile management for all logged-in users
├── admin/
│   └── index.vue           → Admin dashboard: statistics, user management, all properties
├── agency/
│   └── index.vue           → Head Agent dashboard: listings, agent management, reports
├── agent/
│   └── index.vue           → Sub-Agent dashboard: assigned visits and inquiries
├── login.vue               → JWT authentication
└── register.vue            → New user registration
```

#### 6.4.2 State Management & Authentication

Authentication state is managed globally using **Pinia** (`stores/auth.ts`). The store:
- Stores the JWT token and decoded user object.
- Provides computed role-checking helpers (`isAdmin`, `isHeadAgent`, etc.).
- Handles `localStorage` persistence so sessions survive page refreshes.
- Exposes a `logout()` action that clears both the store and the browser storage.

#### 6.4.3 Component Library

Reusable components were organized into 4 families:

| Component Family | Examples |
|---|---|
| `components/property/` | Property cards, image gallery, filter panel |
| `components/ai/` | AI search bar, property Q&A chat interface |
| `components/charts/` | LineChart, BarChart for dashboard analytics |
| `components/agency/` | **TeamCalendar** (Consolidated visit schedule) |
| `components/ui/` | Modal, notification toast, loading skeletons |

#### 6.4.4 Map Integration

Property detail pages include an interactive **Leaflet.js** map that renders the property's GPS coordinates (latitude/longitude stored in PostgreSQL). Clicking the map marker opens the location in Google Maps.

---

### 6.5 Automation Layer — n8n Workflows

Two production n8n workflows were built and are version-controlled as exported JSON files in `n8n_workflows/`.

#### 6.5.1 Workflow 1: Smart Agent Service (Telegram Bot)

**File**: `Elite Estate - Smart Agent service.json`

This is a sophisticated **AI agent** workflow triggered by any Telegram message sent to the bot.

**Architecture** (Multi-Tool AI Agent):
```
Telegram Message Received (Webhook)
         ↓
AI Agent Node (Gemini 1.5 Flash)
         ↓ (uses tools)
┌────────────────────────────────────────┐
│ Tool 1: Search Properties              │
│   → Queries FastAPI /search/rag        │
│   → Returns structured property list  │
│                                        │
│ Tool 2: Get Property Details           │
│   → Fetches full data for a property  │
│                                        │
│ Tool 3: Schedule a Visit               │
│   → POSTs to FastAPI /visits          │
│   → Creates a Google Calendar event   │
│                                        │
│ Tool 4: Get Available Agents           │
│   → Fetches agent list with calendars │
│                                        │
│ Tool 5: PostgreSQL Chat Memory         │
│   → Stores conversation history per   │
│      Telegram user ID                 │
│   → Enables multi-turn conversations  │
└────────────────────────────────────────┘
         ↓
Telegram Reply (formatted response)
```

**Key Technical Achievement**: The agent uses **persistent PostgreSQL memory**, meaning each Telegram user has their own conversation thread. A returning user can say "book the same property as last time" and the agent understands the context.

#### 6.5.2 Workflow 2: Meeting Reminder Service

**File**: `Elite Estate - Meeting Reminder Service (7).json`

This is a **scheduled, polling workflow** that automatically sends visit reminders.

**Logic**:
```
Every Hour (CRON trigger)
         ↓
Query FastAPI for visits scheduled in the next 24 hours
  WHERE reminder_sent = false
         ↓
For each qualifying visit:
  1. Send Telegram message to client (via their telegram_chat_id)
  2. Patch FastAPI: set reminder_sent = true
         ↓
Client receives: "Reminder: Your visit to [Property]
is tomorrow at [Time]. Agent: [Name]."
```

This ensures no appointment is ever missed without any manual effort from the agency staff.

#### 6.5.3 ngrok Tunnel as a Docker Sidecar

A significant engineering challenge was making Telegram's webhook work during development. Telegram's API strictly requires an HTTPS endpoint, but development servers run on `localhost` (HTTP).

**Solution**: An `ngrok` container was added to the `docker-compose.yml` as a **sidecar service**. It creates a permanent HTTPS tunnel (`embryologically-shrewd-may.ngrok-free.dev`) that forwards to the n8n container on port 5678. n8n is then configured with `N8N_PROTOCOL=https` and `N8N_WEBHOOK_URL` pointing to the ngrok domain, making all generated webhook URLs publicly accessible over HTTPS.

---

### 6.6 Cloud Image Management — ImageKit

Property images are stored on **ImageKit.io**, a cloud-based Image CDN, rather than on the local Docker volume. This enables:
- Automatic image optimization and WebP conversion.
- Global CDN delivery (low latency).
- No storage limits on the local development machine.

**Integration**:
- The `imagekitio` Python SDK (`v4.0.0`) is used in `backend/services/storage.py`.
- The frontend uses a `useAssetUrl` composable to render all image URLs correctly, regardless of whether they are absolute CDN URLs or local paths.

**Notable Bug Fixed**: The ImageKit SDK's `upload()` function internally expected an object with a `__dict__` attribute, but the options were passed as a plain Python dictionary. The fix was to wrap the dictionary in `types.SimpleNamespace`, providing the required interface.

---

### 6.7 DevOps — Docker Containerization

The entire platform (5 services) is orchestrated via a single `docker-compose.yml`. Key DevOps decisions:

- **Health Checks**: The `postgres` service has a `pg_isready` health check. The `backend` service uses `depends_on: postgres: condition: service_healthy`, preventing startup race conditions.
- **Named Network**: All services share the `real_estate_network` bridge network, allowing inter-service communication via container names (e.g., `http://backend:8000`).
- **Volume Persistence**: `pg_data/` is mounted to preserve the PostgreSQL database across container restarts.
- **Hot-Reloading**: The `backend` and `frontend` source directories are mounted as bind volumes, enabling live code changes without container rebuilds during development.
- **Environment Variable Management**: All secrets are stored in a `.env` file (never committed to Git). A `.env.example` template is provided for team collaboration.
- **Timezone Configuration**: All containers are configured with `TZ=Africa/Tunis` and mount `/etc/timezone` to ensure consistent timestamps in logs, visit schedules, and Google Calendar events.

---

## 7. Problems Encountered & Solutions Applied

| # | Problem | Root Cause | Solution Applied |
|---|---|---|---|
| 1 | **Telegram webhook rejecting HTTP** | Telegram's API enforces HTTPS-only endpoints | Added ngrok Docker sidecar; set `N8N_PROTOCOL=https` |
| 2 | **n8n webhook URL showing `localhost`** | n8n uses separate vars for internal vs. external routing | Mapped both `WEBHOOK_URL` and `N8N_WEBHOOK_URL` to ngrok domain |
| 3 | **ImageKit SDK `AttributeError: __dict__`** | SDK upload() expected an object, received a Python dict | Wrapped options dict in `types.SimpleNamespace` |
| 4 | **Multi-image upload 404 error** | Frontend sent batch upload to an endpoint that only accepted single files | Implemented new `POST /properties/{id}/images` endpoint accepting `List[UploadFile]` |
| 5 | **Hardcoded localhost image URLs breaking ImageKit** | Frontend was prepending `http://localhost:8000/` to all image paths | Created `useAssetUrl` composable with absolute URL detection logic |
| 6 | **Database startup race condition** | FastAPI started before PostgreSQL was fully ready | Added `service_healthy` condition with `pg_isready` health check |
| 7 | **Google OAuth2 redirect mismatch** | Development and production URLs differed from registered Google Console URIs | Maintained separate `GOOGLE_WEB_CLIENT_ID` (for FastAPI) and `N8N_GOOGLE_CLIENT_ID` (for n8n) |
| 8 | **pgvector embedding dimension mismatch** | Property embeddings stored with 768 dims; search query used different model | Standardized all embedding calls to `nomic-embed-text` via Ollama at 768 dimensions |
| 9 | **Telegram Webhook "Gateway Timeout"** | Communication failure between Telegram and local n8n via ngrok | Implemented tunnel recovery script and updated `WEBHOOK_URL` registration |
| 10 | **Consolidated Team Oversight** | Head Agents lacked a unified view of sub-agent schedules | Built custom TeamCalendar component with multi-agent eager loading |

---

## 8. Results & Validation

### 8.1 Functional Completeness

All planned features from the initial project checklist were successfully implemented and verified:

| Module | Status | Notes |
|---|---|---|
| JWT Authentication & User Registration | ✅ Complete | pbkdf2_sha256 hashing, 60-min token expiry |
| RBAC (4 roles) | ✅ Complete | `RoleChecker` dependency enforced on all protected routes |
| Property CRUD with Multi-Image Upload | ✅ Complete | ImageKit CDN integration, batch upload endpoint |
| AI Semantic Search (pgvector) | ✅ Complete | 768-dim cosine similarity search via Ollama |
| RAG Property Q&A Assistant | ✅ Complete | Gemini 1.5 Pro, property-scoped context |
| Visit Scheduling & Management | ✅ Complete | Sub-agent and head-agent dashboards, **Team Visit Calendar** |
| Transaction Approval Workflow | ✅ Complete | Email notifications, status state machine |
| Telegram AI Bot (5 tools) | ✅ Complete | Multi-turn memory via PostgreSQL |
| Google Calendar Integration | ✅ Complete | OAuth2, event creation on visit booking |
| Meeting Reminder Automation | ✅ Complete | Hourly CRON, Telegram push notification |
| Admin & Analytics Dashboard | ✅ Complete | Platform-wide statistics charts (LineChart, BarChart) |
| Docker Multi-Container Orchestration | ✅ Complete | 5 services, health checks, persistent volumes |

### 8.2 Performance Observations

- **API Response Times**: Standard CRUD endpoints consistently responded under `200ms` locally.
- **Semantic Search Latency**: pgvector cosine similarity queries on the seeded dataset (50+ properties) returned results in under `150ms`.
- **RAG Q&A Latency**: Gemini 1.5 Pro responses averaged `1.5–3 seconds`, acceptable for an interactive chat feature.
- **Telegram Bot**: Average end-to-end response time (message to reply) was `2–4 seconds` depending on the complexity of the AI tool calls.

### 8.3 Security Validation

- **SQL Injection**: Mitigated by SQLAlchemy's ORM — no raw SQL strings are used in application logic.
- **Unauthorized Access**: All sensitive routes were tested with incorrect roles, confirming `HTTP 403` responses.
- **Secret Management**: `.env` is in `.gitignore`; no secrets were committed to the repository.
- **Token Expiry**: Tokens expire after 60 minutes; expired tokens correctly return `HTTP 401`.

---

## 9. UML Documentation

### 9.1 Key User Roles (Use Case Summary)

| Actor | Primary Use Cases |
|---|---|
| **Visitor** | Browse properties, use AI semantic search, view property on map, ask AI assistant, inquire via Telegram |
| **Sub-Agent** | Manage visit requests, confirm visits, update client inquiry status |
| **Head Agent** | Create/edit property listings, upload images, manage sub-agents, approve transactions |
| **Administrator** | Manage all users, view platform statistics, access all properties |
| **Telegram Bot** | Search properties, schedule visits, send reminders (automated actor) |

### 9.2 Core Data Model Summary

```
User (1) ──────────────── (*) Property          [owner]
User (1) ──────────────── (*) Property          [assigned agent]
Property (1) ──────────── (*) PropertyImage
Property (*) ──────────── (*) Feature            [via property_features join table]
Property (1) ──────────── (*) Visit
User (1) ──────────────── (*) Visit              [as client]
User (1) ──────────────── (*) Visit              [as agent]
User (1) ──────────────── (0..1) User            [manager — self-referential]
```

### 9.3 Critical Workflow: Property Listing with AI Embedding

```
[Head Agent] → Submits property form (title, description, features, images)
       ↓
[FastAPI /properties POST]
       ↓
[Validate with Pydantic schemas]
       ↓
[Call Ollama API → nomic-embed-text] → Returns 768-dim float vector
       ↓
[SQLAlchemy INSERT into properties table]
  - All text fields stored normally
  - description_vector stored as Vector(768) in pgvector column
  - Images uploaded to ImageKit → URLs stored in property_images
       ↓
[Property now searchable via both keyword AND semantic similarity]
```

### 9.4 Critical Workflow: Telegram Client Inquiry → Visit Booking

```
[Telegram User] → "I want to visit a 3-bedroom villa in Sfax"
       ↓
[Telegram Trigger in n8n] → Receives message
       ↓
[AI Agent Node — Gemini 1.5 Flash]
  → Invokes Tool: Search Properties
  → Calls FastAPI GET /search/rag?query=...
  → Receives matching properties with agent calendar IDs
       ↓
[AI Agent] → Confirms property and proposes visit time
       ↓
[AI Agent] → Invokes Tool: Schedule Visit
  → POST /visits  (FastAPI creates visit record)
  → Google Calendar API creates event on agent's calendar
  → Stores telegram_chat_id on the visit record
       ↓
[Meeting Reminder Workflow — runs hourly]
  → Finds visit within 24 hours with reminder_sent=false
  → Sends Telegram message to client
  → PATCH /visits/{id}: reminder_sent=true
```

---

## 10. Conclusions & Future Prospects

### 10.1 Summary of Achievements

This project successfully delivered a production-grade, AI-enhanced real estate platform that integrates:
- A **secure, multi-role RESTful API** with proper RBAC and JWT authentication.
- A **relational database with built-in vector search**, eliminating the need for a separate AI infrastructure service.
- A **premium, multi-page web frontend** with role-specific dashboards and an interactive property map.
- An **AI-powered Telegram bot** with persistent memory and 5 callable tools, turning a simple messaging app into a full-featured client engagement channel.
- **Fully automated workflows** for appointment reminders and Google Calendar synchronization.
- A **fully containerized deployment** that can be launched on any machine with Docker in a single command.

### 10.2 Lessons Learned

1. **Architecture Matters from Day One**: The decision to use pgvector within PostgreSQL (rather than adding a separate vector database like Pinecone) was validated — it reduced infrastructure complexity significantly while delivering adequate performance for the project scale.

2. **Docker Networking is a First-Class Engineering Problem**: Configuring inter-service communication, environment variable propagation, health checks, and timezone synchronization across 5 containers required careful planning and iterative debugging.

3. **External API Constraints Shape Architecture**: Telegram's HTTPS-only webhook requirement forced the design of the ngrok sidecar service — a pattern not initially planned but which became a robust, repeatable solution.

4. **Separation of Concerns Enables Collaboration**: The strict division between Member A (platform) and Member B (automation) was possible because the FastAPI REST API served as a well-defined contract between the two domains. Member B's n8n workflows consumed the same API endpoints as the web frontend.

5. **AI Features Require Grounding**: Early prototypes of the RAG assistant returned hallucinated property details. Constraining the Gemini prompt to "answer ONLY from this context" eliminated this problem and made the feature trustworthy and production-safe.

### 10.3 Limitations

- **Ollama Dependency**: The semantic search embedding model runs on the host machine via Ollama. This is not containerized in the current setup, creating a dependency on the development host.
- **Single-Node Deployment**: The current Docker Compose setup is suitable for development and small-scale production but would require migration to Docker Swarm or Kubernetes for high-availability deployment.
- **Telegram-Only Mobile Channel**: The automation layer only supports Telegram. Integration with WhatsApp Business API would significantly expand the client reach in the Tunisian market.
- **No Payment Gateway**: The transaction workflow records and emails approval requests, but actual payment processing is outside the current scope.

### 10.4 Future Prospects

| # | Proposed Enhancement | Technical Approach |
|---|---|---|
| 1 | **Mobile Application** | React Native / Expo, consuming the existing FastAPI REST API |
| 2 | **WhatsApp Bot** | Replace/parallel Telegram channel using WhatsApp Business Cloud API via n8n |
| 3 | **Containerized Ollama** | Add an `ollama` service to `docker-compose.yml` for fully self-contained AI embedding |
| 4 | **Advanced AI Matching** | Proactive match-making: when a new property is listed, automatically notify clients whose search history matches it |
| 5 | **Multi-Language Support** | Add Arabic (RTL) and French versions of the interface for the Tunisian market |
| 6 | **Property Valuation AI** | Train or integrate a regression model to estimate property market value based on historical data |
| 7 | **CI/CD Pipeline** | GitHub Actions workflow to automate testing, image building, and deployment |

---

> **Project Statement**: This project demonstrates that a two-person academic team can architect, build, and deliver a system that combines full-stack web engineering, relational database design with AI extensions, cloud storage integration, production-grade security, and real-time automation — all operating as a unified, containerized platform. The breadth of technologies mastered and integrated during this PFE elevates its scope well beyond a standard end-of-study project.

---

*Document prepared for PFE presentation — Elite Estate Platform*  
*Date: April 2026*

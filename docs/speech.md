# Elite Estate — Presentation Speech (All 49 Slides)
**Duration:** 15–20 minutes | **Presenters:** Isra (I) & Jesser (J)

---

## SLIDE 1 — Title Slide *(unnumbered)*
**[I — Isra]**

Good morning everyone. My name is Isra Hadj Hassine, and alongside my colleague Jesser Chebbi, we are proud to present our graduation project: **Elite Estate** — a Real Estate Automation Platform with a Conversational AI Assistant, developed during our internship at BestTech, under the supervision of Mrs. Yosra Kassis academically, and Mrs. Sonia Ben Aissa on the company side.

---

## SLIDE 2 — Planning *(unnumbered)*
**[I]**

Here is our agenda for today. We will walk you through seven sections: starting with the project context, then our analysis and requirements, followed by each of our four development sprints, and finally our conclusion and perspectives.

---

## SLIDE 3 — Section 01 Divider: Introduction & Context *(unnumbered)*
**[J — Jesser]**

Let's begin with the project's introduction and context.

---

## SLIDE 4 — BestTech IT Services *(page 1)*
**[J]**

BestTech is a Tunisian IT company offering services in web and mobile development, design, and SEO — alongside professional training programs covering web and mobile development, cloud computing, and official Microsoft Azure certifications. It is within this environment that Elite Estate was conceived.

---

## SLIDE 5 — Challenges in Current Real Estate Platforms *(page 2)*
**[J]**

When we analyzed existing real estate platforms in Tunisia, we identified three major problems. First, **inefficient discovery** — users are stuck with rigid filters and cannot search naturally. Second, **manual and time-consuming processes** — agents handle visits, follow-ups, and transactions by hand, which is slow and error-prone. Third, **limited availability** — there is no intelligent system available outside business hours to answer client inquiries.

---

## SLIDE 6 — Proposed Solution — Platform *(page 3)*
**[I]**

Our answer to these challenges is Elite Estate: a multi-role real estate management platform that centralizes property management, automates visit scheduling, and provides a full reporting system for all stakeholders.

---

## SLIDE 7 — Proposed Solution — AI Features *(page 4)*
**[I]**

Beyond the platform itself, we integrated an AI assistant called **TAIA**, which provides 24/7 instant responses, understands client intent through semantic search, and automates workflows like visit booking and reminders — all accessible through Telegram.

---

## SLIDE 8 — Work Methodology: SCRUM *(page 5)*
**[J]**

For our development methodology, we chose **SCRUM**, for three key reasons: its adaptability to change, its iterative and incremental nature, and its clear team structure — which was essential given our 12-week timeline.

---

## SLIDE 9 — SCRUM Team *(page 6)*
**[J]**

Our SCRUM team consisted of Mrs. Sonia Ben Aissa as Product Owner and company supervisor, Mrs. Yosra Kassis as our academic supervisor and SCRUM Master, and ourselves — Isra and Jesser — as the development team.

---

## SLIDE 10 — Sprints Planning *(page 7)*
**[I]**

The project was divided into **four sprints of 3 weeks each**: Sprint 1 for hierarchy and authentication, Sprint 2 for property management, Sprint 3 for the AI pipeline and visit management, and Sprint 4 for transactions and analytics.

---

## SLIDE 11 — Section 02 Divider: Analysis & Requirements *(unnumbered)*
**[I]**

Let's now move into our analysis and requirements specification.

---

## SLIDE 12 — Identification of Actors *(page 9)*
**[I]**

Our platform has five actors: the **Client**, who browses and interacts with properties; the **Sub-Agent**, who handles field visits; the **Head Agent**, who oversees the team and listings; the **Admin**, who controls the platform globally; and **TAIA**, our AI assistant, acting as a secondary actor that interacts across all roles.

---

## SLIDE 13 — Functional Requirements — Client *(page 10)*
**[J]**

For the client, the key features are: browsing properties, booking visits, asking TAIA about properties via Telegram, authenticating, updating their profile, and linking their Telegram account.

---

## SLIDE 14 — Functional Requirements — Admin *(page 11)*
**[J]**

The admin can manage all staff accounts globally, view property listings, receive transaction reports, consult analytics, and receive automated email notifications for key platform events.

---

## SLIDE 15 — Functional Requirements — Head Agent *(page 12)*
**[I]**

The Head Agent manages property listings and sub-agent accounts, consults visits, approves or refuses transaction requests, monitors team performance, and accesses a personal analytics dashboard.

---

## SLIDE 16 — Functional Requirements — Sub-Agent *(page 13)*
**[I]**

The Sub-Agent can consult their assigned properties, view and update visit statuses, manage transaction requests, and receive email responses when a transaction is processed.

---

## SLIDE 17 — Functional Requirements — TAIA *(page 14)*
**[J]**

TAIA is the heart of our AI layer. It can schedule, reschedule, and cancel visits; search properties semantically; pair with Telegram; and send both Telegram messages and email notifications automatically.

---

## SLIDE 18 — Non-Functional Requirements *(page 15)*
**[J]**

Our non-functional requirements cover six pillars: response time, security, scalability, reliability, availability, and usability — ensuring the platform is robust and production-ready.

---

## SLIDE 19 — Technology Stack *(page 16)*
**[I]**

For our technology stack: the frontend uses **Nuxt, Vue, and Tailwind CSS**. The backend is built with **FastAPI** in Python. The database is **PostgreSQL with pgvector** for semantic vector search. Automation workflows run on **n8n**, the infrastructure is containerized with **Docker**, and our AI models combine **Gemini** for language generation and **Ollama** for local embeddings.

---

## SLIDE 20 — Global Use Case Diagram *(page 17)*
**[I]**

This is our global use case diagram, which maps all actors and their interactions across the entire system — giving a comprehensive view of the platform's scope.

---

## SLIDE 21 — Deployment Diagram *(page 18)*
**[J]**

And here is our deployment diagram. The application runs inside Docker Compose containers: a FastAPI backend, a NuxtJS frontend, PostgreSQL database, n8n automation, and an ngrok tunnel to expose the Telegram webhook. External integrations include SMTP for emails, ImageKit for image storage, Telegram API, and OpenRouter for AI model routing.

---

## SLIDE 22 — Section 03 Divider: Sprint 1 — Hierarchy & Authentication *(unnumbered)*
**[J]**

Let's now go through our sprints, starting with Sprint 1: Hierarchy and Authentication.

---

## SLIDE 23 — Use Case Diagram — Sprint 1 *(page 20)*
**[J]**

In this sprint, we covered: visitor registration, admin user management with search and account status toggling, staff account creation, and Head Agent control over Sub-Agent accounts — all secured behind authentication.

---

## SLIDE 24 — Class Diagram — Sprint 1 *(page 21)*
**[I]**

The class diagram shows a **User base class** with subclasses for Client, Admin, HeadAgent, and SubAgent — a clean inheritance structure that captures all roles and their core attributes, including Telegram chat ID for future AI integration.

---

## SLIDE 25 — Sequence Diagram: Authenticate *(page 22)*
**[I]**

The authentication flow is JWT-based: the user submits credentials, the system validates them, checks if the account is active, generates a token, and redirects the user to the correct dashboard based on their role — admin, agency, agent, or client.

---

## SLIDE 26 — Implementation Divider *(unnumbered)*
**[J]**

Let's see Sprint 1 in action.

---

## SLIDE 27 — Implementation Screenshot — Registration *(page 24)*
**[J]**

*(Video plays — ~1 minute)*

Here you can see the registration page and role-based login. Each user is redirected to a different interface upon login depending on their role.

---

## SLIDE 28 — Section 04 Divider: Sprint 2 — Property Management & Catalog Discovery *(unnumbered)*
**[I]**

Sprint 2 focused on property management for agents and catalog discovery for clients.

---

## SLIDE 29 — Use Case Diagram — Sprint 2 *(page 26)*
**[I]**

Visitors and clients can browse the property catalog, view property details and location maps, and filter listings. Head Agents and Sub-Agents can manage their listings — adding, editing, deleting, and uploading images with location pinning on a map.

---

## SLIDE 30 — Class Diagram — Sprint 2 *(page 27)*
**[J]**

The property model is rich: it includes type, listing status, location, pricing, images, and notably a **description vector field** — this is the foundation of our semantic AI search, generated at creation time using Ollama embeddings and stored in pgvector.

---

## SLIDE 31 — Sequence Diagram: Add New Property *(page 28)*
**[J]**

When a Head Agent adds a new property, the system simultaneously generates an embedding from the description using Ollama, uploads the images to ImageKit, and saves all data to the database — in a single coordinated flow.

---

## SLIDE 32 — Implementation Divider *(unnumbered)*
**[I]**

Let's see Sprint 2 in action.

---

## SLIDE 33 — Implementation Screenshot — Property Catalog *(page 30)*
**[I]**

*(Video plays — ~1 minute)*

Here is the property catalog with real listings — a clean card-based UI showing property type, listing type, price, location, and key specs like beds, baths, and surface area.

---

## SLIDE 34 — Section 05 Divider: Sprint 3 — AI Pipeline, TAIA & Visit Management *(unnumbered)*
**[J]**

Sprint 3 is our most technically ambitious sprint — covering the full AI pipeline, the TAIA assistant, and visit management.

---

## SLIDE 35 — Use Case Diagram — Sprint 3 *(page 32)*
**[J]**

In this sprint, clients can interact with TAIA via Telegram to search for properties and schedule, reschedule, or cancel visits. Sub-Agents can view AI-booked visits, update their status, and consult a calendar view. TAIA also sends automated reminder emails to clients before their visits.

---

## SLIDE 36 — Class Diagram — Sprint 3 *(page 33)*
**[I]**

We added two new entities: **Visit** — tracking status, reminder flags, and Telegram chat ID — and **TelegramPairingCode**, which manages the secure pairing between a user's platform account and their Telegram identity through a time-limited code.

---

## SLIDE 37 — Sequence Diagram: RAG Semantic Chat with TAIA *(page 34)*
**[I]**

This is the core of our AI architecture. When a client sends a message to TAIA on Telegram: the query is embedded using Ollama, a vector similarity search is performed on pgvector using L2 distance, the matching properties are retrieved from the database, a RAG response is composed using Gemini, and the final answer is sent back to the client on Telegram — all in real time.

---

## SLIDE 38 — Implementation Divider *(unnumbered)*
**[J]**

Let's see Sprint 3 in action.

---

## SLIDE 39 — Implementation Screenshot — Property Detail + Telegram *(page 36)*
**[J]**

*(Video plays — ~1 minute)*

Here you can see the property detail page with the "Inquire via Telegram" button, and the live Telegram conversation with TAIA handling the full booking flow end-to-end.

---

## SLIDE 40 — Section 06 Divider: Sprint 4 — Transactions, Notifications & Analytics *(unnumbered)*
**[I]**

Our final sprint brought the complete transaction lifecycle, email notifications, and analytics dashboards.

---

## SLIDE 41 — Use Case Diagram — Sprint 4 *(page 38)*
**[I]**

Sub-Agents can request sale or rental transaction approvals from Head Agents. Head Agents can approve or refuse, triggering automated email notifications to all parties. Admins can download PDF transaction reports, consult system-wide analytics, and manage the team calendar.

---

## SLIDE 42 — Class Diagram — Sprint 4 *(page 39)*
**[J]**

We introduced the **TransactionRequest** class, linked to a Visit and a Property, with five possible statuses: pending, approved, rejected, completed, and cancelled — covering the full lifecycle of a real estate transaction.

---

## SLIDE 43 — Sequence Diagram: Download Transaction Reports *(page 40)*
**[J]**

When an admin requests a report download, the system fetches it by ID, generates a structured PDF through the report service, and returns the file directly for download — all triggered in a single action.

---

## SLIDE 44 — Implementation Divider *(unnumbered)*
**[I]**

Let's see Sprint 4 in action.

---

## SLIDE 45 — Implementation Screenshot — Agent Workspace *(page 42)*
**[I]**

*(Video plays — ~1 minute)*

Here is the Agent Workspace dashboard, showing live visit tracking with filters, the property portfolio, calendar view, and performance analytics — giving agents complete visibility over their operations.

---

## SLIDE 46 — Section 07 Divider: Conclusion & Perspectives *(unnumbered)*
**[J]**

Let's wrap up with our conclusion and perspectives.

---

## SLIDE 47 — Conclusion *(page 44)*
**[J]**

Elite Estate successfully delivers: **agile delivery** through four structured SCRUM sprints, a **centralized platform** unifying all real estate stakeholders, an **AI-powered assistant** accessible 24/7 via Telegram, **automated workflows** for visits and notifications, and a **complete transaction lifecycle** from first inquiry to final deal.

---

## SLIDE 48 — Perspectives *(page 45)*
**[I]**

Looking ahead, we envision: **smart contract generation** for automated legal documents, **cloud deployment** for scalability, **CRM integration** for better lead management, **personalized AI recommendations** based on client history, and a **mobile application** to extend access to all users.

---

## SLIDE 49 — Thank You *(unnumbered)*
**[Both]**

**[I]:** This project has been a deeply enriching experience — technically and professionally. We are proud of what we built and grateful for the guidance we received throughout.

**[J]:** We are now open to your questions. Thank you very much for your attention.

---

*Estimated speaking time: ~14–16 minutes + ~4 minutes of videos = within the 15–20 minute window.*
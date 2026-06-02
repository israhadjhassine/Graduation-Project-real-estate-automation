# Internship & PFE Realizations Guide

This guide compiles the technical choices, research investigations, engineering resolutions, and outcomes realized during the internship / PFE project.

---

## 1. Project Context and Objectives

The objective of this PFE was to develop **Elite Estate**, an automated real estate platform. Traditional real estate systems rely on manual communication (calls, emails) to schedule properties and match clients, leading to missed opportunities and administrative delays.

### Core Goals
1. **Interactive Real Estate Portal**: Allow clients to browse and book property visits online, and give agents dashboards to manage schedules, track listings, and finalize transactions.
2. **Conversational AI Agent (Chatbot)**: Offer a Telegram chatbot allowing clients to pair their account, search listings using natural language, check agent schedules, and book visits.
3. **Automated Notification Engine**: Prevent missing appointments by implementing an automated reminder system alerting clients (Telegram) and agents (Email) prior to scheduled viewings.

---

## 2. Technical Stack Justifications

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Frontend** | **Nuxt 4 / Vue 3** | Combines Vite speed, directory-based routing, Pinia state stores, and Tailwind CSS. Nuxt 4 structures code into clean layers (`app/components`, `app/pages`, `app/stores`), decoupling client logic. |
| **Backend** | **FastAPI** | High-performance asynchronous Python API. Offers native JSON request validation via Pydantic, auto-generated OpenAPI documentation, and fast execution speeds. |
| **Database** | **PostgreSQL + `pgvector`** | Keeps relational tables and vector embeddings in a single ACID-compliant database. Prevents synchronization lag inherent in external vector DBs (e.g., Pinecone). |
| **Automation** | **n8n (Self-hosted)** | Visual node-based workflow builder that manages LLM chains, database transactions, webhook listeners, and cron schedules with minimal overhead. |
| **Embeddings** | **Gemini API** | Uses `text-embedding-004` to output 768-dimensional float arrays from property titles and descriptions for semantic search. |
| **LLM Model** | **DeepSeek-V4-Flash** | Invoked via OpenRouter inside the n8n agent. Provides exceptional reasoning and tool-calling capabilities at low latency and cost. |

---

## 3. RAG vs. Keyword Search: Core Findings

During research phases, we compared keyword-based relational search against Retrieval-Augmented Generation (RAG) vector search.

### Keyword Search (SQL `ilike` / Indexing)
* **Mechanics**: Matches substrings directly (e.g. `WHERE title ILIKE '%Marsa%'`).
* **Strengths**: Perfect for exact matches, filters (e.g., matching bedrooms = 3, price <= 2500 TND).
* **Weaknesses**: Fragile. Fails to understand context or synonyms (e.g., searching "house with garden" will miss properties described as "villa with spacious backyard").

### RAG Semantic Search (`pgvector` Cosine Distance)
* **Mechanics**: Converts property descriptions into 768-dimensional vector arrays. Queries are embedded and compared using cosine distance operator (`<=>`).
* **Strengths**: Understands synonyms and concepts (e.g., associates "backyard" with "garden", "luxury" with high price).
* **Weaknesses**: Cannot easily enforce hard logic constraints (e.g., filtering out apartments priced above 1000 TND unless explicit pre-filtering is done).

### Architectural Conclusion
Elite Estate utilizes a **Hybrid Search Architecture**:
1. **Web Portal**: Relies on structured keyword search and metadata filters (`/search/semantic` endpoint) for exact matching.
2. **Telegram Agent**: Uses RAG vector search (`/search/rag` endpoint) to deliver conversational, natural language responses.

---

## 4. Technical Challenges Resolved

### Challenge 1: ngrok Local Tunneling for Webhooks
* **Issue**: The Telegram bot and n8n require HTTPS endpoints to communicate. Local docker containers run on HTTP and are not visible to external API gateways.
* **Solution**: Configured **ngrok** to tunnel traffic to the local network port (`ngrok http 8000`). Mapped the resulting public HTTPS URL (e.g. `https://xxxx.ngrok-free.app`) to the n8n node configuration, enabling external webhook triggers and callback handlers.

### Challenge 2: Timezone Synchronization
* **Issue**: Date/time strings sent from client browsers (in local Tunis time or ISO UTC formats) were causing database mismatch checks. Some scheduled visits occurred in UTC, while agent availability routines checked local Tunisian time (UTC+1), resulting in false overlap conflicts and time shift bugs.
* **Solution**: Standardized all database storage to **naive UTC**. We created a timezone translation pipeline inside `/visits/agent-availability`:
  1. Parse input date strings and check for UTC offsets (`Z` or `+00:00`). If naive, assume `Africa/Tunis` local timezone.
  2. Convert the timestamp to UTC (`astimezone(timezone.utc).replace(tzinfo=None)`) before performing DB comparisons.
  3. Re-convert UTC timestamps back to `Africa/Tunis` (UTC+1) for working hour validation (ensuring slots fall between 06:00 and 22:00 local Tunis time, and on weekdays only).

### Challenge 3: ImageKit SDK Dictionary Serialization Bug
* **Issue**: When uploading listings images, the ImageKit Python SDK `imagekit.upload_file()` did not return a plain dictionary. Instead, it returned a custom Python model object. Passing this object directly to a handler trying to index values (`result['url']`) raised attribute errors, and returning it directly failed Pydantic schema validation.
* **Solution**: Wrapped the upload handler response in an attribute inspection wrapper in `backend/services/storage.py`:
  ```python
  url = None
  f_id = None
  if hasattr(result, 'url'):
      url = result.url
      f_id = result.file_id if hasattr(result, 'file_id') else None
  elif isinstance(result, dict):
      url = result.get('url')
      f_id = result.get('fileId')
  ```
  This ensures that both structured model objects and fallback dictionaries are normalized to a consistent python dictionary `{"url": url, "file_id": f_id}` prior to returning.

---

## 5. Internship Conclusions

The PFE project successfully integrated automated pipelines into a real estate management system. By combining Nuxt 4 web portals with n8n workflow managers and LLMs, we reduced scheduling delays and improved agent response times.

### Lessons Learned
* **Workflow Decoupling**: Offloading conversational dialog states and scheduled timers to n8n kept the FastAPI codebase lean, fast, and simple.
* **Database Cohesion**: Using PostgreSQL and `pgvector` proved that dedicated vector search can be implemented alongside standard relational schemas, avoiding operational overhead.
* **Data Security**: Encrypting sensitive chat IDs using deterministic AES-256-CBC demonstrated how developer-friendly search lookups can be maintained without compromising user privacy.

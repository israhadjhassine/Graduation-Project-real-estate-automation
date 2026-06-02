# n8n Workflow Integration Documentation

This document describes the design, nodes, and configurations of the production n8n workflows supporting the **Elite Estate** platform.

---

## 1. Overview of n8n Engine

Elite Estate uses a self-hosted **n8n** container to coordinate asynchronous tasks. Rather than coding complex chatbot flows or scheduler loops in Python, n8n orchestrates:
1. **Interactive AI Conversations**: Bridging Telegram updates, LangChain memories, and tool APIs.
2. **Time-Based Reminders**: Running minute-level checks, querying upcoming events, and triggering communications across email and messaging channels.

---

## 2. Workflow 1: Smart Agent Service (Telegram Bot)

* **Filename**: `n8n_workflows/Elite Estate - Smart Agent service (6).json`
* **Trigger**: **Telegram Trigger Node** (Webhook listening for `message`).
* **Core Agent Node**: **AI Agent (LangChain)** (`n8n-nodes-langchain.agent`).
* **Model**: **DeepSeek-V4-Flash** (`deepseek/deepseek-v4-flash`) configured via OpenRouter.
* **Memory**: **Postgres Chat Memory** (`n8n-nodes-langchain.memoryPostgresChat`).

### Chatbot Architecture

```text
  [Telegram User Message]
            │
            ▼
┌───────────────────────┐
│  Telegram Webhook     │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│     AI Agent Node     │ ◄───► [Postgres Chat Memory]
│  (DeepSeek-V4-Flash)  │       (Session Key: {{ $json.message.chat.id }})
└─────┬───────────┬─────┘
      │           │
      ▼           ▼
[ LangChain Custom HTTP Tools ]
  ├─► pair_telegram
  ├─► search_properties
  ├─► check_agent_availability
  ├─► book_visit
  ├─► update_visit_db
  └─► cancel_visit_db
            │
            ▼
  [Telegram Reply Message]
```

### Conversational Memory

To allow multi-turn dialogue, the workflow uses a **Postgres Chat Memory** node connected to the project's PostgreSQL database:
* **Session ID**: Mapped to the Telegram Chat ID: `{{ $json.message.chat.id }}`.
* **Table**: `conversation_history` (stores message roles, text, and timestamps).
* **Benefit**: The user can say "Is the villa still available?" followed by "Book a visit for tomorrow at 2 PM", and the agent retains the specific property context.

---

### LangChain HTTP Agent Tools

The AI Agent utilizes **6 custom HTTP tools** to interact with the FastAPI backend. Each tool is configured to send payloads to the API and return text responses.

#### 1. `pair_telegram`
* **Description**: Pairs a visitor's Telegram account to their registered web profile using a 6-digit verification code.
* **Input Schema**:
  ```json
  {
    "code": "string (6-digit code, optionally prefixed by pair_)",
    "telegram_chat_id": "string (Telegram Chat ID of current user)"
  }
  ```
* **Endpoint**: `POST /auth/telegram/pair`
* **Response**: Returns JSON indicating success and the user's name (e.g., `{"status": "success", "user_name": "Jesse"}`).

#### 2. `search_properties`
* **Description**: Searches property listings using RAG. Returns property details matching a query string.
* **Input Schema**:
  ```json
  {
    "query": "string (semantic search query, e.g., 'villa with pool in La Marsa')"
  }
  ```
* **Endpoint**: `POST /search/rag` (Uses Gemini embeddings and `pgvector` similarity).
* **Response**: Context block containing property titles, descriptions, status, pricing, and coordinates.

#### 3. `check_agent_availability`
* **Description**: Verifies if an agent has free slots for scheduling a visit.
* **Input Schema**:
  ```json
  {
    "agent_id": "integer",
    "visit_date": "string (ISO format: YYYY-MM-DDTHH:MM:SS)"
  }
  ```
* **Endpoint**: `POST /visits/agent-availability`
* **Response**: Returns a boolean `is_available` and a list of 5 alternative recommended time slots.

#### 4. `book_visit`
* **Description**: Books a viewing appointment in the database.
* **Input Schema**:
  ```json
  {
    "property_id": "integer",
    "client_telegram_id": "string (Telegram Chat ID)",
    "agent_id": "integer",
    "visit_date": "string (ISO format: YYYY-MM-DDTHH:MM:SS)"
  }
  ```
* **Endpoint**: `POST /visits/book`
* **Response**: Details of the newly created booking.

#### 5. `update_visit_db`
* **Description**: Reschedules an existing scheduled visit.
* **Input Schema**:
  ```json
  {
    "client_telegram_id": "string (Telegram Chat ID)",
    "property_id": "integer",
    "original_visit_date": "string (ISO format)",
    "new_visit_date": "string (ISO format)"
  }
  ```
* **Endpoint**: `PUT /visits/update`
* **Response**: Details of the updated scheduling record.

#### 6. `cancel_visit_db`
* **Description**: Cancels a scheduled visit.
* **Input Schema**:
  ```json
  {
    "client_telegram_id": "string (Telegram Chat ID)",
    "property_id": "integer",
    "visit_date": "string (ISO format)"
  }
  ```
* **Endpoint**: `POST /visits/cancel`
* **Response**: Success status message.

---

## 3. Workflow 2: Meeting Reminder Service

* **Filename**: `n8n_workflows/Elite Estate - Meeting Reminder Service (9).json`
* **Trigger**: **Schedule Trigger Node** (CRON scheduled to execute **every 1 minute**).
* **Target Window**: Checks for visits scheduled in the next 24 hours.

### Execution Flow

```text
   [Cron Trigger: Every 1 Minute]
                 │
                 ▼
      [GET /visits/upcoming]
                 │
                 ▼
       [Split In Batches] (Loops over each upcoming visit)
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
[Send client Telegram]  [Send agent SMTP Email]
(uses decrypted ID)    (uses HTML template)
       │                   │
       └─────────┬─────────┘
                 │
                 ▼
  [PUT /visits/{id}/reminder-sent]
```

### Node Specifications

1. **Schedule Trigger**: Fires every minute. This frequent interval ensures immediate alerting and prevents race conditions with short-notice test appointments.
2. **HTTP Request (Fetch Visits)**:
   * **Endpoint**: `GET /visits/upcoming`
   * **Response**: A JSON array of visits falling within a 24-hour lookahead window. Since the backend `schemas.VisitDetailResponse` automatically decrypts the `telegram_chat_id`, the JSON payload contains the client's plaintext Telegram ID.
3. **Split in Batches**: Iterates sequentially over the retrieved visits list.
4. **Client Reminder (Telegram Bot)**:
   * **Node Type**: Telegram Bot node.
   * **Chat ID**: Mapped dynamically from `{{ $json.telegram_chat_id }}`.
   * **Message**: Formatted in Markdown notifying the client of the property name, location, scheduled time, and assigned agent.
5. **Agent Reminder (Email Notification)**:
   * **Node Type**: SMTP Send Email node.
   * **Recipient**: Sent to the sub-agent's email: `{{ $json.agent.email }}`.
   * **Content**: Custom HTML email detailing the client's contact info, scheduled visit date, and listing specifications.
6. **HTTP Request (Mark Notified)**:
   * **Endpoint**: `PUT /visits/{{ $json.id }}/reminder-sent`
   * **Purpose**: Sets `reminder_sent = true` in the PostgreSQL database. This prevents subsequent cron runs from notifying the same users.

---

## 4. Environment & Integration Configuration

### ngrok Local Tunneling
For external services (Telegram, n8n) to communicate with the local FastAPI backend, an HTTPS tunnel must be established.
* **Command**: `ngrok http 8000`
* **Setup**: The resulting public URL (e.g., `https://xxxx.ngrok-free.app`) must be configured as the base URL inside n8n's HTTP Request nodes (replacing `localhost:8000`).

### Telegram Bot Hook
* The Telegram bot requires registering the webhook URL pointing to the n8n trigger endpoint:
  `https://<n8n-domain>/webhook/v1/telegram`
* Both `TELEGRAM_BOT_TOKEN` and the Webhook URL are declared in n8n's credentials manager.

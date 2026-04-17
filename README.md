# Elite Estate: AI-Driven Real Estate Automation

A premium, modular real estate platform that leverages AI (Gemini + RAG) and advanced automation (n8n + Telegram) to streamline property management and appointment scheduling.

## 🌟 Core Features

-   **Modular Backend**: Professionally organized FastAPI architecture using the Service-Router pattern.
-   **AI Assistant (RAG)**: Retrieval-Augmented Generation for intelligent property Q&A using Gemini Pro and `pgvector`.
-   **Automated Scheduling**: Real-time Google Calendar synchronization via n8n and Telegram.
-   **Smart Reporting**: Automated transaction reports and lead management.
-   **Premium UI**: High-performance frontend built with Nuxt 3 and Tailwind CSS.

## 🛠 Tech Stack

-   **Backend**: FastAPI (Python), SQLAlchemy, PostgreSQL/pgvector.
-   **AI**: Google Gemini Pro (1.5), Ollama (Local Embeddings).
-   **Automation**: n8n, Telegram Bot API.
-   **Cloud/Storage**: ImageKit.io.
-   **Frontend**: Nuxt 3, Vue 3, Tailwind CSS.
-   **Infrastructure**: Docker, Docker Compose.

## 🚀 Getting Started

1.  **Environment Setup**: Copy `.env.example` to `.env` and fill in your API keys (Gemini, ImageKit, SMTP).
2.  **Launch Services**: Run `docker-compose up -d`.
3.  **Access App**:
    -   Frontend: [http://localhost:3000](http://localhost:3000)
    -   Backend API: [http://localhost:8000/docs](http://localhost:8000/docs)
    -   n8n: [http://localhost:5678](http://localhost:5678)

For more detailed information, see the [Architecture Overview](file:///docs/ARCHITECTURE.md).
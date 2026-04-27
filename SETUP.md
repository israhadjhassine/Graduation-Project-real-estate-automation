# 🏠 Elite Estate: Local Setup Guide

Follow these steps to get the full Elite Estate stack running on your local machine.

## 🛠 Prerequisites

Ensure you have the following installed:
- **Docker & Docker Compose**: For running the entire stack.
- **Ollama**: For local AI embeddings (runs on your host machine).
- **ngrok account**: Required for Telegram bot webhooks.

---

## 1. Local AI Embeddings (Ollama)

Ollama runs on your host machine to leverage your system's performance.

1.  **Install Ollama**: Download from [ollama.com](https://ollama.com/).
2.  **Install Model**: Run the following in your terminal:
    ```bash
    ollama pull nomic-embed-text
    ```
3.  **Cross-Container Access**: 
    - On Windows, ensuring Ollama is running is usually enough.
    - If you see "Connection Refused" errors, set the environment variable `OLLAMA_HOST=0.0.0.0` on your Windows system and restart Ollama.

---

## 2. Setting up n8n & Telegram (ngrok)

To allow Telegram to talk to your local n8n instance, you need a public tunnel.

### Step A: ngrok Free Domain
1.  Sign up at [ngrok.com](https://ngrok.com/).
2.  Go to the **Cloud Edge > Domains** section.
3.  Click **Create Domain** (you get one free static domain).
4.  Copy your domain (e.g., `your-name.ngrok-free.app`).

### Step B: n8n Configuration
1.  Get your `NGROK_AUTHTOKEN` from the ngrok dashboard.
2.  Update these values in your `.env` to match your ngrok domain:
    ```bash
    NGROK_AUTHTOKEN=your_token_here
    N8N_HOST=your-name.ngrok-free.app
    WEBHOOK_URL=https://your-name.ngrok-free.app
    N8N_EDITOR_BASE_URL=https://your-name.ngrok-free.app
    ```

---

## 3. AI & External Services

We use **OpenRouter** for the AI Agent to keep it flexible and free for testing.

1.  **OpenRouter**:
    - Sign up at [openrouter.ai](https://openrouter.ai/).
    - Create an API Key.
    - In the n8n **Smart Agent** workflow, choose the model: `google/gemini-2.0-flash-001`.
2.  **Telegram**: Create a bot via [@BotFather](https://t.me/botfather) and copy the token.
3.  **ImageKit.io**: Register a free account to handle property images.
4.  **Google Calendar**: enable the Calendar API in [Google Cloud Console](https://console.cloud.google.com/) and create OAuth 2.0 Credentials.

> [!NOTE]
> You do **not** need a direct Google Gemini API key if you are using OpenRouter.

---

## 4. Launching the App

1.  **Configure `.env`**:
    ```bash
    cp .env.example .env
    # Fill in OpenRouter, Telegram, ImageKit, and ngrok details.
    ```
2.  **Start Docker**:
    ```bash
    docker-compose up -d --build
    ```
3.  **Seed Database**:
    ```bash
    docker exec -it FastAPI_backend python seed.py
    ```

### Access Points:
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **n8n Agent**: [http://localhost:5678](http://localhost:5678)

---

## 🔍 Troubleshooting

- **Ollama Error**: Check if the service is running (`ollama list` should show `nomic-embed-text`).
- **Telegram Bot Error**: Confirm your `WEBHOOK_URL` in `.env` matches your ngrok domain.

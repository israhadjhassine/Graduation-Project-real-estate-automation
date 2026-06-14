# Elite Estate: Local Setup Guide

Follow these steps to get the full Elite Estate stack running on your local machine.

## Prerequisites

Ensure you have the following installed:
- **Docker & Docker Compose**: For running the entire stack.
- **Ollama**: For local AI embeddings (runs on your host machine).
- **ngrok account**: Required for Telegram bot webhooks and secure external access.

---

## 1. Local AI Embeddings (Ollama)

Ollama runs on your host machine to leverage your system's performance for generating vector embeddings.

1.  **Install Ollama**: Download from [ollama.com](https://ollama.com/).
2.  **Install Model**: Run the following in your terminal to download the embedding model:
    ```bash
    ollama pull nomic-embed-text
    ```
3.  **Cross-Container Access**: 
    - On Windows, ensure Ollama is running in the background.
    - If you encounter "Connection Refused" errors from the backend, set the system environment variable `OLLAMA_HOST=0.0.0.0` and restart the Ollama application.

---

## 2. Setting up n8n & External Access (ngrok)

To allow Telegram to communicate with your local n8n instance and access the n8n editor via the web, you must set up a public tunnel.

### Step A: Create an ngrok Free Domain
1.  Sign up at [ngrok.com](https://ngrok.com/).
2.  Navigate to **Cloud Edge > Domains**.
3.  Click **Create Domain** (one static domain is free per account).
4.  Copy your domain (e.g., `your-name.ngrok-free.app`).

### Step B: Configure n8n in .env
1.  Retrieve your `NGROK_AUTHTOKEN` from the ngrok dashboard.
2.  Update your `.env` file with these values:
    ```bash
    NGROK_AUTHTOKEN=your_token_here
    N8N_HOST=your-name.ngrok-free.app
    WEBHOOK_URL=https://your-name.ngrok-free.app
    N8N_EDITOR_BASE_URL=https://your-name.ngrok-free.app
    ```
3.  **Note**: Once the stack is running, you will access the n8n dashboard using your ngrok link: `https://your-name.ngrok-free.app`.

---

## 3. External Services Configuration

### 3.1 ImageKit.io (Media Management)
ImageKit handles property images via a global CDN.
1.  Register at [imagekit.io](https://imagekit.io/).
2.  In the dashboard, go to **Developer Options**.
3.  Copy the following into your `.env`:
    - `IMAGEKIT_PUBLIC_KEY`
    - `IMAGEKIT_PRIVATE_KEY`
    - `IMAGEKIT_URL_ENDPOINT` (e.g., `https://ik.imagekit.io/your_id/`)

### 3.2 OpenRouter (AI Agent)
1.  Sign up at [openrouter.ai](https://openrouter.ai/).
2.  Create an API Key and add it to `.env` as `OPENROUTER_API_KEY`.
3.  In the n8n **Smart Agent** workflow, ensure the model is set to `deepseek/deepseek-v4-flash` via OpenRouter.

### 3.3 Telegram Bot
1.  Message [@BotFather](https://t.me/botfather) to create a new bot.
2.  Copy the **API Token** into your `.env`.

---

## 4. Launching the Application

1.  **Prepare Environment**:
    ```bash
    cp .env.example .env
    # Ensure all keys from the steps above are filled in.
    ```
2.  **Start the Stack**:
    ```bash
    docker-compose up -d --build
    ```
3.  **Initialize the Database**:
    ```bash
    docker exec -it FastAPI_backend python seed.py
    ```

### Access Points:
- **Frontend Dashboard**: [http://localhost:3000](http://localhost:3000)
- **Interactive API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **n8n Automation Editor**: `https://your-name.ngrok-free.app` (Using your ngrok tunnel)

---

## Troubleshooting

- **Ollama Error**: Run `ollama list` to verify `nomic-embed-text` is installed.
- **Telegram Webhook**: If the bot doesn't respond, check the `WEBHOOK_URL` in `.env` and ensure it uses `https://`.

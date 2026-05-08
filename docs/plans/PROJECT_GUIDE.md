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

### 3.2 Google Cloud Console (Calendar API)
Required for synchronizing property visits with agent calendars.
1.  Go to [Google Cloud Console](https://console.cloud.google.com/).
2.  **Create a Project**: Select "New Project" and give it a name.
3.  **Enable API**: Search for "Google Calendar API" and click **Enable**.
4.  **OAuth Consent Screen**:
    - Go to **APIs & Services > OAuth consent screen**.
    - Choose "External" and fill in the required app information and support email.
5.  **Create Credentials**:
    - Go to **APIs & Services > Credentials**.
    - Click **Create Credentials > OAuth client ID**.
    - Application type: **Web application**.
    - **Authorized Redirect URIs**: Add `https://your-name.ngrok-free.app/rest/oauth2-callback`.
6.  Copy the **Client ID** and **Client Secret** (you will use these in the next step).

### 3.3 Connecting Google Calendar in n8n
Once n8n is running, you must link it to your Google account.
1.  Open your n8n editor (`https://your-name.ngrok-free.app`).
2.  Open the **Smart Agent** or **Reminder** workflow.
3.  Click on any **Google Calendar node**.
4.  In the **Credential** dropdown, select **Create New Credential**.
5.  Authentication Method: Select **OAuth2**.
6.  Enter the **Client ID** and **Client Secret** from the Google Cloud Console.
7.  Click **Sign in with Google** and authorize the application.

### 3.4 OpenRouter (AI Agent)
1.  Sign up at [openrouter.ai](https://openrouter.ai/).
2.  Create an API Key and add it to `.env` as `OPENROUTER_API_KEY`.
3.  In the n8n **Smart Agent** workflow, ensure the model is set to `google/gemini-2.0-flash-001`.

### 3.5 Telegram Bot
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
- **Google OAuth**: Ensure the redirect URI in Google Console exactly matches the one in your `.env` (including the `/rest/oauth2-callback` suffix).

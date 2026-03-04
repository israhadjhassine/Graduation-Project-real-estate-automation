# Guide: Telegram & n8n Automation Setup

This guide provides full instructions on how the n8n automation was configured to support Telegram webhooks using ngrok as a secure tunnel, including solutions for common errors encountered during setup.

## 1. Prerequisites
- **ngrok Account**: Required for getting a public HTTPS URL. Sign up at [ngrok.com](https://ngrok.com).
- **Telegram Bot**: Created via `@BotFather` to get your `TELEGRAM_BOT_TOKEN`.

## 2. Infrastructure Setup (Docker)

### ngrok Service
```yaml
  ngrok:
    image: ngrok/ngrok:latest
    restart: always
    environment:
      NGROK_AUTHTOKEN: ${NGROK_AUTHTOKEN}
    command:
      - "http"
      - "n8n_automation:5678"
    ports:
      - "4040:4040"
    networks:
      - real_estate_network
```

### n8n Service
The `n8n` service was updated with specific environment variables to handle the ngrok tunnel:

```yaml
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n_automation
    restart: always
    environment:
      - N8N_BASIC_AUTH_USER=${N8N_BASIC_AUTH_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_BASIC_AUTH_PASSWORD}
      - WEBHOOK_URL=${WEBHOOK_URL}
      - N8N_WEBHOOK_URL=${WEBHOOK_URL}
      - N8N_EDITOR_BASE_URL=${WEBHOOK_URL}
      - N8N_PROTOCOL=https
      # ... other variables (DB, Gemini, etc.)
    networks:
      - real_estate_network
```

## 3. Environment Configuration (.env)

The following variables must be present in your `.env` file:

```env
# ngrok authentication
NGROK_AUTHTOKEN=your_secret_token

# Telegram Bot Token
TELEGRAM_BOT_TOKEN=your_bot_token

# Public URL (retrieved from ngrok)
WEBHOOK_URL=https://your-unique-id.ngrok-free.dev
```

## 4. n8n Configuration Variables

To ensure n8n uses the secure tunnel for webhooks, these environment variables are mapped in the `n8n` service:

- `N8N_WEBHOOK_URL`: Forces n8n to generate production webhook URLs using the ngrok address.
- `N8N_PROTOCOL=https`: **Critical** for Telegram, which only allows HTTPS.
- `N8N_EDITOR_BASE_URL`: Sets the public address for the n8n UI.

## 5. Troubleshooting & Lessons Learned

During the integration, we faced and resolved several issues. Use these steps if errors reappear:

### ⚠️ Error: ERR_NGROK_4018 (Authentication Failed)
- **Symptom**: `docker logs ngrok` shows "authentication failed" or "verified account required".
- **Cause**: The `NGROK_AUTHTOKEN` is missing from the environment.
- **Troubleshoot**: Ensure the token is in the file literally named `.env`. A common mistake is adding it to `.env.example` which Docker ignores.
- **Fix**: Move the token to `.env` and run `docker-compose up -d ngrok`.

### ⚠️ Error: Bad Request: An HTTPS URL must be provided
- **Symptom**: n8n displays a "Bad Request" popup when activating the Telegram Trigger.
- **Cause**: Telegram's API refuses to send webhooks to non-HTTPS (HTTP) addresses.
- **Troubleshoot**: Verify that your `WEBHOOK_URL` in `.env` starts with `https://`.
- **Fix**: Add `N8N_PROTOCOL=https` to your n8n environment variables in `docker-compose.yml`.

### ⚠️ Error: Production URL is still "localhost"
- **Symptom**: Test events work, but the "Production URL" tab in n8n shows `http://localhost:5678` instead of ngrok.
- **Cause**: n8n uses different variables for internal vs. external routing.
- **Fix**: In `docker-compose.yml`, you must explicitly map both `N8N_WEBHOOK_URL` and the plain `WEBHOOK_URL` to your ngrok address.

## 6. How to Activate Telegram Webhooks

1. **Start Tunnel**: `docker-compose up -d ngrok`.
2. **Retrieve URL**: Run in PowerShell:
   ```powershell
   powershell -Command "(Invoke-RestMethod -Uri http://localhost:4040/api/tunnels).tunnels[0].public_url"
   ```
3. **Update .env**: Paste the new URL into `WEBHOOK_URL`.
4. **Restart n8n**: `docker-compose up -d --force-recreate n8n`.
5. **Activate**: Re-open the Telegram Trigger node and click **Activate**.

---
> [!TIP]
> **Why did we do this?**
> Local servers (localhost) cannot be reached by Telegram. ngrok creates a "bridge" from the public internet to your local Docker container, allowing Telegram to send lead notifications directly to your workflow.

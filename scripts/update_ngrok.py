import urllib.request
import json
import re
import os
import subprocess

# Configuration
NGROK_API_URL = "http://localhost:4040/api/tunnels"
ENV_FILE_PATH = ".env"

def get_ngrok_url():
    try:
        with urllib.request.urlopen(NGROK_API_URL) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                # Find the first https tunnel
                for tunnel in data['tunnels']:
                    if tunnel['proto'] == 'https':
                        return tunnel['public_url']
            else:
                print(f"❌ Error: ngrok API returned status {response.status}")
    except Exception as e:
        print(f"❌ Error fetching ngrok URL: {e}")
        return None
    return None

def update_env_file(new_url):
    if not os.path.exists(ENV_FILE_PATH):
        print(f"❌ {ENV_FILE_PATH} not found!")
        return False

    with open(ENV_FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update WEBHOOK_URL
    content = re.sub(r'WEBHOOK_URL=.*', f'WEBHOOK_URL={new_url}', content)
    
    # Update N8N_GOOGLE_REDIRECT_URI
    redirect_uri = f"{new_url}/rest/oauth2-credential/callback"
    content = re.sub(r'N8N_GOOGLE_REDIRECT_URI=.*', f'N8N_GOOGLE_REDIRECT_URI={redirect_uri}', content)

    with open(ENV_FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated {ENV_FILE_PATH} with {new_url}")
    return True

def restart_n8n():
    print("🔄 Restarting n8n to apply changes...")
    try:
        # Using shell=True for Windows compatibility with docker-compose command
        subprocess.run("docker-compose up -d --force-recreate n8n", shell=True, check=True)
        print("✅ n8n restarted successfully.")
    except Exception as e:
        print(f"❌ Failed to restart n8n: {e}")

if __name__ == "__main__":
    print("🔍 Fetching new ngrok URL...")
    url = get_ngrok_url()
    if url:
        if update_env_file(url):
            restart_n8n()
    else:
        print("💡 Make sure your ngrok container is running and healthy!")

import sys
import requests
from datetime import datetime, timedelta, timezone

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

def get_valid_property(property_id):
    try:
        r = requests.get(f"{BASE_URL}/properties")
        if r.status_code != 200:
            return None
        properties = r.json()
        for prop in properties:
            if prop["id"] == property_id:
                return prop
        # Fallback to first property if specified id not found
        if properties:
            return properties[0]
    except Exception as e:
        print(f"Error connecting to backend: {e}")
    return None

def main():
    if len(sys.argv) < 2:
        print("\n❌ Error: Please provide your Telegram Chat ID.")
        print("Usage: python scripts/test_reminder.py <YOUR_TELEGRAM_CHAT_ID> [PROPERTY_ID]")
        print("Example: python scripts/test_reminder.py 123456789\n")
        sys.exit(1)
        
    chat_id = sys.argv[1]
    property_id = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    
    print("🔍 Fetching property and agent details from database...")
    prop = get_valid_property(property_id)
    if not prop:
        print("❌ Error: Could not find any properties in the database. Ensure seed is run.")
        sys.exit(1)
        
    actual_prop_id = prop["id"]
    agent_id = prop["agent_id"]
    print(f"✅ Found property: '{prop['title']}' (ID: {actual_prop_id}) managed by Agent (ID: {agent_id})")
    
    # Calculate a date 2 hours in the future (within the 24-hour upcoming window)
    # Ensure it is a weekday since the endpoint restricts weekend bookings
    visit_dt = datetime.now(timezone.utc) + timedelta(hours=2)
    # If today is Saturday or Sunday, move it to Monday
    if visit_dt.weekday() == 5: # Saturday
        visit_dt += timedelta(days=2)
    elif visit_dt.weekday() == 6: # Sunday
        visit_dt += timedelta(days=1)
        
    visit_date_str = visit_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    payload = {
        "property_id": actual_prop_id,
        "client_telegram_id": str(chat_id),
        "agent_id": agent_id,
        "visit_date": visit_date_str
    }
    
    print(f"📅 Booking visit for: {visit_date_str}...")
    try:
        r = requests.post(f"{BASE_URL}/visits/book", json=payload)
        if r.status_code == 200:
            visit = r.json()
            print("\n🎉 Visit booked successfully!")
            print(f"• Visit ID: {visit['id']}")
            print(f"• Property ID: {visit['property_id']}")
            print(f"• Agent ID: {visit['agent_id']}")
            print(f"• Telegram Chat ID: {visit['telegram_chat_id']} (Stored securely & encrypted)")
            print(f"• Visit Date: {visit['visit_date']}")
            print("\n👉 To trigger the reminder immediately in n8n:")
            print("1. Open n8n (http://localhost:5678)")
            print("2. Open the workflow 'Elite Estate - Meeting Reminder Service'")
            print("3. Click 'Execute Workflow' at the bottom of the canvas.")
            print("4. Check your Telegram Bot - you should receive the reminder instantly!")
        else:
            print(f"❌ Failed to book visit: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    main()

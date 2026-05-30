import requests
import sys
import json
import datetime
from datetime import timedelta

# Import database and models
sys.path.append("/app")
import database
import models

BASE_URL = "http://localhost:8000"
db = next(database.get_db())

# Ensure Agent 3 exists
agent = db.query(models.User).filter(models.User.id == 3).first()
if not agent:
    print("❌ ERROR: Agent ID 3 not found in DB.")
    sys.exit(1)

tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

print("==================================================")
print("   COMPREHENSIVE AVAILABILITY ENDPOINT TESTS      ")
print("==================================================")

def run_test_case(name, requested_date, expected_status=200):
    print(f"\n👉 TEST CASE: {name}")
    print(f"Querying for date/time: '{requested_date}'")
    url = f"{BASE_URL}/visits/agent-availability"
    params = {"agent_id": 3, "requested_date": requested_date}
    res = requests.get(url, params=params)
    print(f"Status: {res.status_code}")
    if res.status_code == expected_status:
        data = res.json()
        print(f"is_available: {data.get('is_available')}")
        print(f"available_slots (first 3): {data.get('available_slots', [])[:3]}")
        return data
    else:
        print(f"Error payload: {res.text}")
        return None

# Case 1: Naive Date Only
run_test_case("Naive Date Only (YYYY-MM-DD)", tomorrow)

# Case 2: Naive Datetime
run_test_case("Naive Datetime", f"{tomorrow}T14:30:00")

# Case 3: UTC Aware Datetime (ends with Z)
run_test_case("UTC Aware Datetime (Z)", f"{tomorrow}T14:30:00Z")

# Case 4: Offset Aware Datetime (+01:00)
run_test_case("Offset Aware Datetime (+01:00)", f"{tomorrow}T14:30:00+01:00")

# Case 5: Outside Working Hours (4:00 AM local Tunis time)
run_test_case("Outside Working Hours (04:00 Tunis time)", f"{tomorrow}T04:00:00")

# Case 6: Invalid Format
run_test_case("Invalid Date Format", "not-a-date", expected_status=400)

# Case 7: Conflict & Overlap Check
print("\n👉 TEST CASE: Booking Overlap & Conflict Checks")
target_slot = f"{tomorrow}T11:00:00+01:00"
print(f"Booking a temporary visit for Agent 3 at {target_slot}...")
book_payload = {
    "property_id": 1,
    "client_telegram_id": "123456789",
    "agent_id": 3,
    "visit_date": target_slot
}
book_res = requests.post(f"{BASE_URL}/visits/book", json=book_payload)
if book_res.status_code == 200:
    booked_visit_id = book_res.json()["id"]
    print(f"Successfully booked visit ID: {booked_visit_id}")
    
    # 7a. Query exact slot
    print(f"\nChecking exact slot availability for {target_slot}...")
    res_exact = requests.get(f"{BASE_URL}/visits/agent-availability", params={"agent_id": 3, "requested_date": target_slot})
    print(f"Exact slot response: is_available = {res_exact.json().get('is_available')}")
    
    # 7b. Query conflicting slot within 1 hour (e.g. 11:30)
    conflict_slot = f"{tomorrow}T11:30:00+01:00"
    print(f"\nChecking conflicting slot (within 1 hour) for {conflict_slot}...")
    res_conflict = requests.get(f"{BASE_URL}/visits/agent-availability", params={"agent_id": 3, "requested_date": conflict_slot})
    print(f"Conflicting slot response: is_available = {res_conflict.json().get('is_available')}")
    
    # 7c. Query non-conflicting slot (e.g. 13:00)
    free_slot = f"{tomorrow}T13:00:00+01:00"
    print(f"\nChecking non-conflicting slot for {free_slot}...")
    res_free = requests.get(f"{BASE_URL}/visits/agent-availability", params={"agent_id": 3, "requested_date": free_slot})
    print(f"Non-conflicting slot response: is_available = {res_free.json().get('is_available')}")
    
    # Clean up
    db.query(models.Visit).filter(models.Visit.id == booked_visit_id).delete()
    db.commit()
    print("\nTemporary visit cleaned up.")
else:
    print(f"❌ Booking failed: {book_res.text}")

# Case 8: Past Datetime (should cap to 'now' and return future slots only)
past_date = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%dT10:00:00")
run_test_case("Past Datetime (should not return past slots)", past_date)

import sys
import os
import requests
from datetime import datetime, timedelta, timezone

# Add parent directory to sys.path to import local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Property, User, Visit, TransactionRequest

def run_test():
    print("=== STARTING TRANSACTION FLOW INTEGRATION TEST ===")
    db = SessionLocal()
    try:
        # 1. Fetch required entities
        ocean_breeze = db.query(Property).filter(Property.title == 'Ocean Breeze Mansion').first()
        ahmed = db.query(User).filter(User.email == 'killer.chebbi@gmail.com').first()
        hedi = db.query(User).filter(User.email == 'h.kallel@elite.tn').first()
        client = db.query(User).filter(User.email == 'client@test.com').first()

        if not (ocean_breeze and ahmed and hedi and client):
            print("❌ Test setup failed: missing property, agents, or client in DB.")
            sys.exit(1)

        print(f"Loaded ocean_breeze (ID: {ocean_breeze.id}), ahmed (ID: {ahmed.id}), hedi (ID: {hedi.id}), client (ID: {client.id})")

        # Reset state for clean run
        # Remove any existing transaction requests
        db.query(TransactionRequest).filter(TransactionRequest.property_id == ocean_breeze.id).delete()
        ocean_breeze.status = "available"
        ocean_breeze.agent_id = ahmed.id
        
        # Ensure we have visits in the scheduled state
        db.query(Visit).filter(Visit.property_id == ocean_breeze.id).delete()
        
        today_10am = datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0)
        today_430pm = datetime.now(timezone.utc).replace(hour=16, minute=30, second=0, microsecond=0)
        
        visit1 = Visit(
            property_id=ocean_breeze.id,
            client_id=client.id,
            agent_id=ahmed.id,
            visit_date=today_10am,
            status="scheduled"
        )
        visit2 = Visit(
            property_id=ocean_breeze.id,
            client_id=client.id,
            agent_id=ahmed.id,
            visit_date=today_430pm,
            status="scheduled"
        )
        db.add(visit1)
        db.add(visit2)
        db.commit()
        db.refresh(visit1)
        db.refresh(visit2)

        print("✅ DB Reset complete. 2 scheduled visits created.")

        # 2. Login as Ahmed (Sub-agent)
        login_res = requests.post(
            "http://127.0.0.1:8000/auth/login",
            data={"username": "killer.chebbi@gmail.com", "password": "agentpassword"}
        )
        if login_res.status_code != 200:
            print(f"❌ Login for Ahmed failed: {login_res.text}")
            sys.exit(1)
        ahmed_token = login_res.json()["access_token"]
        ahmed_headers = {"Authorization": f"Bearer {ahmed_token}"}
        print("✅ Ahmed (sub-agent) logged in successfully.")

        # 3. Request Sale (expecting FAILURE because no visits are finished yet)
        request_body = {
            "type": "Sale",
            "price": 1200000.0,
            "client_id": client.id
        }
        req_res1 = requests.post(
            f"http://127.0.0.1:8000/properties/{ocean_breeze.id}/request-transaction",
            json=request_body,
            headers=ahmed_headers
        )
        print(f"Attempting sale request before visit completed. Status code: {req_res1.status_code}")
        if req_res1.status_code == 400:
            print(f"✅ Success! Correctly blocked with message: {req_res1.json()['detail']}")
        else:
            print(f"❌ Failed: expected status code 400, got {req_res1.status_code}. Response: {req_res1.text}")
            sys.exit(1)

        # 4. Mark first visit as finished
        # Endpoint: PUT /agent/visits/{visit_id}/status?status=finished
        visit_res = requests.put(
            f"http://127.0.0.1:8000/agent/visits/{visit1.id}/status?status=finished",
            headers=ahmed_headers
        )
        if visit_res.status_code != 200:
            print(f"❌ Failed to mark visit as finished: {visit_res.text}")
            sys.exit(1)
        db.refresh(visit1)
        print(f"✅ Visit 1 marked as {visit1.status}.")

        # 5. Request Sale again (expecting SUCCESS)
        req_res2 = requests.post(
            f"http://127.0.0.1:8000/properties/{ocean_breeze.id}/request-transaction",
            json=request_body,
            headers=ahmed_headers
        )
        print(f"Attempting sale request after visit completed. Status code: {req_res2.status_code}")
        if req_res2.status_code == 200:
            print("✅ Success! Sale request submitted.")
        else:
            print(f"❌ Failed to submit sale request: {req_res2.text}")
            sys.exit(1)

        db.refresh(ocean_breeze)
        print(f"Property status is now: {ocean_breeze.status} (Expected: pending_sold)")
        assert ocean_breeze.status == "pending_sold", f"Unexpected property status: {ocean_breeze.status}"

        # 6. Login as Hedi Kallel (Head Agent)
        login_res_hedi = requests.post(
            "http://127.0.0.1:8000/auth/login",
            data={"username": "h.kallel@elite.tn", "password": "managerpassword"}
        )
        if login_res_hedi.status_code != 200:
            print(f"❌ Login for Hedi failed: {login_res_hedi.text}")
            sys.exit(1)
        hedi_token = login_res_hedi.json()["access_token"]
        hedi_headers = {"Authorization": f"Bearer {hedi_token}"}
        print("✅ Hedi (head agent) logged in successfully.")

        # Find the inquiry/transaction request ID
        inq = db.query(TransactionRequest).filter(
            TransactionRequest.property_id == ocean_breeze.id,
            TransactionRequest.status == "pending"
        ).first()
        if not inq:
            print("❌ Failed: TransactionRequest not found in database.")
            sys.exit(1)
        
        # Approve the request (status=replied)
        # Endpoint: PUT /agent/inquiries/{inquiry_id}/status?status=replied
        approve_res = requests.put(
            f"http://127.0.0.1:8000/agent/inquiries/{inq.id}/status?status=replied",
            headers=hedi_headers
        )
        print(f"Approving transaction request. Status code: {approve_res.status_code}")
        if approve_res.status_code == 200:
            print("✅ Success! Transaction request approved.")
        else:
            print(f"❌ Failed to approve transaction request: {approve_res.text}")
            sys.exit(1)

        db.refresh(ocean_breeze)
        db.refresh(inq)
        print(f"Transaction Request status is now: {inq.status} (Expected: approved)")
        print(f"Property status is now: {ocean_breeze.status} (Expected: approved_sold)")
        assert inq.status == "approved"
        assert ocean_breeze.status == "approved_sold"

        # 7. Finalize transaction as Ahmed (complete)
        # Endpoint: POST /properties/{property_id}/finalize-transaction
        # Body: {"action": "complete"}
        finalize_res = requests.post(
            f"http://127.0.0.1:8000/properties/{ocean_breeze.id}/finalize-transaction",
            json={"action": "complete"},
            headers=ahmed_headers
        )
        print(f"Finalizing transaction. Status code: {finalize_res.status_code}")
        if finalize_res.status_code == 200:
            print(f"✅ Success! Transaction completed. Response: {finalize_res.json()['message']}")
        else:
            print(f"❌ Failed to finalize transaction: {finalize_res.text}")
            sys.exit(1)

        db.refresh(ocean_breeze)
        db.refresh(inq)
        db.refresh(visit2)

        print(f"Final property status: {ocean_breeze.status} (Expected: sold)")
        print(f"Final Transaction Request status: {inq.status} (Expected: completed)")
        print(f"Final Visit 2 (at 16:30) status: {visit2.status} (Expected: cancelled)")

        assert ocean_breeze.status == "sold", f"Expected sold, got {ocean_breeze.status}"
        assert inq.status == "completed", f"Expected completed, got {inq.status}"
        assert visit2.status == "cancelled", f"Expected cancelled, got {visit2.status}"

        # 8. Test cancellation path
        print("\n--- Testing Transaction Request Cancellation Flow ---")
        # Reset state for cancellation test
        db.query(TransactionRequest).filter(TransactionRequest.property_id == ocean_breeze.id).delete()
        ocean_breeze.status = "available"
        visit1.status = "finished"
        db.commit()

        # Submit new sale request
        req_res_cancel = requests.post(
            f"http://127.0.0.1:8000/properties/{ocean_breeze.id}/request-transaction",
            json=request_body,
            headers=ahmed_headers
        )
        if req_res_cancel.status_code != 200:
            print(f"❌ Failed to submit sale request for cancel test: {req_res_cancel.text}")
            sys.exit(1)

        db.refresh(ocean_breeze)
        assert ocean_breeze.status == "pending_sold"

        # Approve it as head agent
        inq_cancel = db.query(TransactionRequest).filter(
            TransactionRequest.property_id == ocean_breeze.id,
            TransactionRequest.status == "pending"
        ).first()
        
        approve_res_cancel = requests.put(
            f"http://127.0.0.1:8000/agent/inquiries/{inq_cancel.id}/status?status=replied",
            headers=hedi_headers
        )
        if approve_res_cancel.status_code != 200:
            print(f"❌ Failed to approve transaction request for cancel test: {approve_res_cancel.text}")
            sys.exit(1)

        db.refresh(ocean_breeze)
        db.refresh(inq_cancel)
        assert ocean_breeze.status == "approved_sold"
        assert inq_cancel.status == "approved"

        # Finalize as CANCEL as Ahmed
        finalize_cancel_res = requests.post(
            f"http://127.0.0.1:8000/properties/{ocean_breeze.id}/finalize-transaction",
            json={"action": "cancel"},
            headers=ahmed_headers
        )
        print(f"Cancelling transaction. Status code: {finalize_cancel_res.status_code}")
        if finalize_cancel_res.status_code == 200:
            print(f"✅ Success! Transaction cancelled. Response: {finalize_cancel_res.json()['message']}")
        else:
            print(f"❌ Failed to cancel transaction: {finalize_cancel_res.text}")
            sys.exit(1)

        db.refresh(ocean_breeze)
        db.refresh(inq_cancel)
        print(f"Property status after cancel: {ocean_breeze.status} (Expected: available)")
        print(f"Transaction Request status after cancel: {inq_cancel.status} (Expected: cancelled)")
        assert ocean_breeze.status == "available"
        assert inq_cancel.status == "cancelled"

        print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! 🎉")

    except Exception as e:
        print(f"❌ Error during integration test: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    run_test()

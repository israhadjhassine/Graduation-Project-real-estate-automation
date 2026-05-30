import sys
import os

# Adjust path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import email

if __name__ == "__main__":
    print("Testing SMTP email dispatch from the backend...")
    target_email = "killer.chebbi@gmail.com"
    print(f"Sending test account status email to: {target_email}")
    
    # Try sending an activation email
    email.send_account_status_email(
        user_email=target_email,
        user_name="Jesse",
        is_active=True,
        manager_name="System SMTP Test"
    )
    print("Execution completed. Check the console output above for success or connection errors.")

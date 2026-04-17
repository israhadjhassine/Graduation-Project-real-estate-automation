import smtplib
import os
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

def send_transaction_request_email(
    head_agent_email: str,
    head_agent_name: str,
    sub_agent_name: str,
    sub_agent_email: str,
    property_title: str,
    property_location: str,
    property_price: str,
    tx_type: str,  # "Sale" or "Rent"
    client_email: str = None,
    rent_start: str = None,
    rent_end: str = None,
):
    """Sends an HTML email to the Head Agent notifying them of a pending transaction request."""
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    email_from = os.getenv("EMAIL_FROM", smtp_user)

    # Debug: print config (mask password)
    print(f"[EMAIL DEBUG] server={smtp_server} port={smtp_port} user='{smtp_user}' password_len={len(smtp_password)} from='{email_from}'", flush=True)

    try:
        subject = f"⏳ Approval Required: {tx_type} Request for '{property_title}'"

        rent_block = ""
        if tx_type == "Rent" and rent_start and rent_end:
            rent_block = f"""
            <tr>
              <td style="padding:6px 0;color:#6b7280;font-size:13px;">Rent Duration</td>
              <td style="padding:6px 0;font-weight:600;font-size:13px;">{rent_start} → {rent_end}</td>
            </tr>"""

        client_block = ""
        if client_email:
            client_block = f"""
            <tr>
              <td style="padding:6px 0;color:#6b7280;font-size:13px;">Client Email</td>
              <td style="padding:6px 0;font-weight:600;font-size:13px;">{client_email}</td>
            </tr>"""

        tx_color = "#16a34a" if tx_type == "Sale" else "#2563eb"
        tx_badge = f'<span style="background:{tx_color};color:#fff;padding:4px 12px;border-radius:99px;font-size:12px;font-weight:700;">{tx_type.upper()} REQUEST</span>'

        html = f"""
        <!DOCTYPE html>
        <html>
        <body style="margin:0;padding:0;background:#f3f4f6;font-family:'Segoe UI',sans-serif;">
          <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 20px;">
            <tr><td align="center">
              <table width="580" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">
                <tr>
                   <td style="background:linear-gradient(135deg,#1e293b,#334155);padding:32px 40px;">
                    <p style="margin:0;color:#94a3b8;font-size:12px;letter-spacing:2px;text-transform:uppercase;">Elite Estate Platform</p>
                    <h1 style="margin:8px 0 0;color:#ffffff;font-size:22px;font-weight:700;">Transaction Approval Needed</h1>
                  </td>
                </tr>
                <tr>
                  <td style="padding:36px 40px;">
                    <p style="margin:0 0 20px;color:#374151;font-size:15px;">
                      Hi <strong>{{head_agent_name}}</strong>, a sub-agent on your team has submitted a new approval request:
                    </p>
                    <p style="margin:0 0 24px;">{{tx_badge}}</p>
                    <table cellpadding="0" cellspacing="0" width="100%" style="border-top:1px solid #e5e7eb;border-bottom:1px solid #e5e7eb;margin-bottom:24px;">
                      <tr>
                        <td style="padding:6px 0;color:#6b7280;font-size:13px;width:40%;">Sub-Agent</td>
                        <td style="padding:6px 0;font-weight:600;font-size:13px;">{{sub_agent_name}} ({{sub_agent_email}})</td>
                      </tr>
                      <tr>
                        <td style="padding:6px 0;color:#6b7280;font-size:13px;">Property</td>
                        <td style="padding:6px 0;font-weight:600;font-size:13px;">{{property_title}}</td>
                      </tr>
                      <tr>
                        <td style="padding:6px 0;color:#6b7280;font-size:13px;">Location</td>
                        <td style="padding:6px 0;font-weight:600;font-size:13px;">{{property_location}}</td>
                      </tr>
                      <tr>
                        <td style="padding:6px 0;color:#6b7280;font-size:13px;">Price</td>
                        <td style="padding:6px 0;font-weight:600;font-size:13px;">{{property_price}}</td>
                      </tr>
                      {{client_block}}
                      {{rent_block}}
                      <tr>
                        <td style="padding:6px 0;color:#6b7280;font-size:13px;">Requested At</td>
                        <td style="padding:6px 0;font-weight:600;font-size:13px;">{{datetime.now().strftime('%Y-%m-%d %H:%M')}}</td>
                      </tr>
                    </table>
                    <p style="margin:0;color:#6b7280;font-size:13px;">
                      Please log in to the <strong>Agency Dashboard</strong> → <em>Notifications</em> tab to approve or reject this request.
                    </p>
                  </td>
                </tr>
                <tr>
                  <td style="background:#f8fafc;padding:20px 40px;border-top:1px solid #e5e7eb;">
                    <p style="margin:0;color:#9ca3af;font-size:12px;">
                      This is an automated notification from the Elite Estate platform. Do not reply directly to this email.
                    </p>
                  </td>
                </tr>
              </table>
            </td></tr>
          </table>
        </body>
        </html>
        """.replace("{{head_agent_name}}", str(head_agent_name)).replace("{{tx_badge}}", str(tx_badge)).replace("{{sub_agent_name}}", str(sub_agent_name)).replace("{{sub_agent_email}}", str(sub_agent_email)).replace("{{property_title}}", str(property_title)).replace("{{property_location}}", str(property_location)).replace("{{property_price}}", str(property_price)).replace("{{client_block}}", str(client_block)).replace("{{rent_block}}", str(rent_block)).replace("{{datetime.now().strftime('%Y-%m-%d %H:%M')}}", datetime.now().strftime('%Y-%m-%d %H:%M'))

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = email_from
        msg["To"] = head_agent_email
        msg.attach(MIMEText(html, "html"))

        try:
            print(f"[EMAIL DEBUG] Trying STARTTLS on port {smtp_port}...", flush=True)
            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                server.ehlo(); server.starttls(); server.ehlo()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, head_agent_email, msg.as_string())
        except smtplib.SMTPAuthenticationError as auth_err:
            print(f"[EMAIL DEBUG] STARTTLS auth failed ({auth_err}), trying SSL on port 465...", flush=True)
            with smtplib.SMTP_SSL(smtp_server, 465, timeout=10) as server:
                server.ehlo()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, head_agent_email, msg.as_string())

        print(f"[EMAIL] ✅ Sent {tx_type} request notification to {head_agent_email}", flush=True)
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send notification email: {e}", flush=True)
        traceback.print_exc()

def send_admin_report_email(admin_email: str, admin_name: str, property_title: str, tx_type: str, pdf_path: str):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    email_from = os.getenv("EMAIL_FROM", smtp_user)

    try:
        subject = f"📑 New Transaction Finalized: {property_title} ({tx_type})"
        html = f"""
        <!DOCTYPE html>
        <html>
        <body style="margin:0;padding:0;background:#f3f4f6;font-family:'Segoe UI',sans-serif;">
          <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 20px;">
            <tr><td align="center">
              <table width="580" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">
                <tr>
                  <td style="background:linear-gradient(135deg,#1e293b,#334155);padding:32px 40px;">
                    <p style="margin:0;color:#94a3b8;font-size:12px;letter-spacing:2px;text-transform:uppercase;">Admin Notification</p>
                    <h1 style="margin:8px 0 0;color:#ffffff;font-size:22px;font-weight:700;">Transaction Report Ready</h1>
                  </td>
                </tr>
                <tr>
                  <td style="padding:36px 40px;">
                    <p style="margin:0 0 20px;color:#374151;font-size:15px;">
                      Hi <strong>{{admin_name}}</strong>,
                    </p>
                    <p style="margin:0 0 20px;color:#374151;font-size:15px;">
                      A new <strong>{{tx_type}}</strong> transaction has been officially approved and finalized for the property: <strong>{{property_title}}</strong>.
                    </p>
                    <p style="margin:0 0 20px;color:#374151;font-size:15px;">
                      Please find the detailed transaction report attached to this email as a PDF.
                    </p>
                  </td>
                </tr>
                <tr>
                  <td style="background:#f8fafc;padding:20px 40px;border-top:1px solid #e5e7eb;">
                    <p style="margin:0;color:#9ca3af;font-size:12px;">Elite Estate Management System</p>
                  </td>
                </tr>
              </table>
            </td></tr>
          </table>
        </body>
        </html>
        """.replace("{{admin_name}}", str(admin_name)).replace("{{tx_type}}", str(tx_type)).replace("{{property_title}}", str(property_title))

        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = email_from
        msg["To"] = admin_email
        msg.attach(MIMEText(html, "html"))

        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(pdf_path)}")
                msg.attach(part)

        try:
            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                server.ehlo(); server.starttls(); server.ehlo()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, admin_email, msg.as_string())
        except Exception:
            with smtplib.SMTP_SSL(smtp_server, 465, timeout=10) as server:
                server.ehlo()
                server.login(smtp_user, smtp_password)
                server.sendmail(smtp_user, admin_email, msg.as_string())
        print(f"[EMAIL] ✅ Report sent to Admin: {admin_email}", flush=True)
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send Admin report email: {e}", flush=True)
        traceback.print_exc()

def send_account_status_email(user_email: str, user_name: str, is_active: bool, manager_name: str):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    email_from = os.getenv("EMAIL_FROM", smtp_user)
    status_text = "ACTIVATED" if is_active else "DEACTIVATED"
    status_color = "#16a34a" if is_active else "#dc2626"
    action_description = "You now have full access to your dashboard." if is_active else "Your access to the platform has been temporarily restricted."

    try:
        subject = f"🔔 Account Status Update: Your account has been {status_text}"
        html = f"""<!DOCTYPE html><html><body style="margin:0;padding:0;background:#f3f4f6;font-family:'Segoe UI',sans-serif;">
          <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 20px;"><tr><td align="center">
              <table width="580" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">
                <tr><td style="background:linear-gradient(135deg,#1e293b,#334155);padding:32px 40px;">
                    <h1 style="margin:8px 0 0;color:#ffffff;font-size:22px;font-weight:700;">Account {{status_text}}</h1>
                  </td></tr>
                <tr><td style="padding:36px 40px;"><p>Hi <strong>{{user_name}}</strong>,</p><p>Status update by <strong>{{manager_name}}</strong>.</p>
                    <div style="background:#f8fafc;padding:24px;text-align:center;border:1px solid #e5e7eb;"><span style="color:{{status_color}};font-weight:800;">{{status_text}}</span></div>
                  </td></tr>
              </table></td></tr></table></body></html>""".replace("{{status_text}}", str(status_text)).replace("{{user_name}}", str(user_name)).replace("{{manager_name}}", str(manager_name)).replace("{{status_color}}", str(status_color))
        msg = MIMEMultipart(); msg["Subject"] = subject; msg["From"] = email_from; msg["To"] = user_email
        msg.attach(MIMEText(html, "html"))
        try:
            with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
                server.ehlo(); server.starttls(); server.ehlo(); server.login(smtp_user, smtp_password); server.sendmail(smtp_user, user_email, msg.as_string())
        except Exception:
            with smtplib.SMTP_SSL(smtp_server, 465, timeout=10) as server:
                server.ehlo(); server.login(smtp_user, smtp_password); server.sendmail(smtp_user, user_email, msg.as_string())
        print(f"[EMAIL] ✅ Account {status_text} email sent", flush=True)
    except Exception as e:
        print(f"[EMAIL ERROR] {e}", flush=True)

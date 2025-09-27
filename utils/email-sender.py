# utils/email_sender.py
import os
from config import SENDGRID_API_KEY
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email_sendgrid(to_email: str, subject: str, plain_text: str, html_content: str = None):
    """
    Send email via SendGrid. Requires SENDGRID_API_KEY in env.
    Returns True on success, False otherwise.
    """
    if not SENDGRID_API_KEY:
        print("SENDGRID_API_KEY not configured. Email will not be sent. Message:\n", plain_text)
        return False

    message = Mail(
        from_email='no-reply@patternprotect.example.com',
        to_emails=to_email,
        subject=subject,
        plain_text_content=plain_text,
        html_content=html_content or plain_text
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        # 2xx status codes indicate success
        return 200 <= response.status_code < 300
    except Exception as e:
        print("SendGrid error:", e)
        return False

def send_delivery_email(to_email: str, buyer_name: str, download_link: str, pattern_name: str, expiry_hours: int = 24):
    subject = f"Your pattern: {pattern_name} — download link"
    body = f"Hi {buyer_name},\n\nThank you for your purchase. Download your pattern here:\n\n{download_link}\n\nThis link expires in {expiry_hours} hours.\n\nRegards,\nPatternProtect (delivered by seller)\n"
    sent = send_email_sendgrid(to_email, subject, body)
    if not sent:
        # fallback: print to console so seller can copy/paste
        print("=== EMAIL FALLBACK ===")
        print(body)
        print("======================")
        return False
    return True

import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


def send_email(to_email: str, subject: str, body: str) -> None:
    """Send an email through the Mailtrap testing SMTP server."""

    host = os.getenv("SMTP_HOST", "sandbox.smtp.mailtrap.io")
    port = int(os.getenv("SMTP_PORT", "2525"))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")

    if not username or not password:
        raise RuntimeError("Mailtrap SMTP credentials are not configured.")

    email = EmailMessage()
    email["Subject"] = subject
    email["From"] = os.getenv("EMAIL_FROM", "test@example.com")
    email["To"] = to_email
    email.set_content(body)

    with smtplib.SMTP(host, port, timeout=20) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(email)
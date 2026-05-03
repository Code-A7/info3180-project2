import smtplib
import time
from email.message import EmailMessage

from flask import current_app


def _get_mail_config():
    return {
        "host": current_app.config.get("SMTP_HOST")
        or current_app.config.get("MAILTRAP_SMTP_HOST"),
        "port": current_app.config.get("SMTP_PORT")
        or current_app.config.get("MAILTRAP_SMTP_PORT"),
        "user": current_app.config.get("SMTP_USER")
        or current_app.config.get("MAILTRAP_SMTP_USER"),
        "password": current_app.config.get("SMTP_PASS")
        or current_app.config.get("MAILTRAP_SMTP_PASS"),
        "from_email": current_app.config.get("SMTP_FROM_EMAIL")
        or current_app.config.get("MAILTRAP_FROM_EMAIL"),
        "use_tls": current_app.config.get("SMTP_USE_TLS", True),
        "use_ssl": current_app.config.get("SMTP_USE_SSL", False),
    }


def send_email(to_email, subject, body):
    """Send an HTML email using configured SMTP settings."""
    if not current_app.config.get("TESTING"):
        time.sleep(1)
    else:
        print(f"[MOCK EMAIL] To: {to_email}, Subject: {subject}")
        print(f"[MOCK EMAIL] Body: {body[:200]}...")
        return True

    mail_config = _get_mail_config()
    if not mail_config["user"] or not mail_config["password"]:
        if current_app.config.get("TESTING") or current_app.config.get("DEBUG"):
            print(f"[MOCK EMAIL] To: {to_email}, Subject: {subject}")
            print(f"[MOCK EMAIL] Body: {body[:200]}...")
            return True

        print("[EMAIL ERROR] SMTP_USER/SMTP_PASS are not configured")
        return False

    try:
        print(
            f"[EMAIL] Attempting to send to {to_email} "
            f"via {mail_config['host']}:{mail_config['port']}"
        )

        msg = EmailMessage()
        msg["From"] = mail_config["from_email"]
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content("Please view this email in an HTML-compatible email client.")
        msg.add_alternative(body, subtype="html")

        smtp_class = smtplib.SMTP_SSL if mail_config["use_ssl"] else smtplib.SMTP
        with smtp_class(mail_config["host"], mail_config["port"], timeout=10) as server:
            if mail_config["use_tls"] and not mail_config["use_ssl"]:
                server.starttls()
            server.login(mail_config["user"], mail_config["password"])
            server.send_message(msg)

        print(f"[EMAIL] Successfully sent to {to_email}")
        return True
    except Exception as exc:
        print(f"[EMAIL ERROR] Failed to send email to {to_email}: {exc}")
        return False

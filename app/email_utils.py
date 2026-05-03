import smtplib
import time
import json
from email.message import EmailMessage
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

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


def _send_resend_email(to_email, subject, body):
    api_key = current_app.config.get("RESEND_API_KEY")
    api_url = current_app.config.get("RESEND_API_URL")
    from_email = current_app.config.get("EMAIL_FROM") or current_app.config.get(
        "SMTP_FROM_EMAIL"
    )

    if not api_key:
        print("[EMAIL ERROR] RESEND_API_KEY is not configured")
        return False

    payload = json.dumps(
        {
            "from": from_email,
            "to": [to_email],
            "subject": subject,
            "html": body,
        }
    ).encode("utf-8")

    request = Request(
        api_url,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        print(f"[EMAIL] Attempting to send to {to_email} via Resend API")
        with urlopen(request, timeout=10) as response:
            if 200 <= response.status < 300:
                print(f"[EMAIL] Successfully sent to {to_email}")
                return True

            print(f"[EMAIL ERROR] Resend returned status {response.status}")
            return False
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        print(f"[EMAIL ERROR] Resend returned {exc.code}: {error_body}")
        return False
    except URLError as exc:
        print(f"[EMAIL ERROR] Failed to reach Resend API: {exc.reason}")
        return False
    except Exception as exc:
        print(f"[EMAIL ERROR] Failed to send email to {to_email}: {exc}")
        return False


def _send_smtp_email(to_email, subject, body):
    mail_config = _get_mail_config()
    if not mail_config["user"] or not mail_config["password"]:
        if current_app.config.get("DEBUG"):
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


def send_email(to_email, subject, body):
    """Send an HTML email using the configured provider."""
    if not current_app.config.get("TESTING"):
        time.sleep(1)
    else:
        print(f"[MOCK EMAIL] To: {to_email}, Subject: {subject}")
        print(f"[MOCK EMAIL] Body: {body[:200]}...")
        return True

    provider = current_app.config.get("EMAIL_PROVIDER", "smtp").lower()
    if provider == "resend":
        return _send_resend_email(to_email, subject, body)

    return _send_smtp_email(to_email, subject, body)

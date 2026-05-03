import os

from app import create_app, socketio

if __name__ == "__main__":
    os.environ["EMAIL_PROVIDER"] = os.environ.get("LOCAL_EMAIL_PROVIDER", "smtp")
    os.environ["SMTP_HOST"] = os.environ.get(
        "LOCAL_SMTP_HOST", os.environ.get("SMTP_HOST", "")
    )
    os.environ["SMTP_PORT"] = os.environ.get(
        "LOCAL_SMTP_PORT", os.environ.get("SMTP_PORT", "")
    )
    os.environ["SMTP_USER"] = os.environ.get(
        "LOCAL_SMTP_USER", os.environ.get("SMTP_USER", "")
    )
    os.environ["SMTP_PASS"] = os.environ.get(
        "LOCAL_SMTP_PASS", os.environ.get("SMTP_PASS", "")
    )
    os.environ["SMTP_FROM_EMAIL"] = os.environ.get(
        "LOCAL_SMTP_FROM_EMAIL", os.environ.get("SMTP_FROM_EMAIL", "")
    )

app = create_app()

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)

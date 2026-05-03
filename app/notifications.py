import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Blueprint, current_app, jsonify

from app import db
from app.models import Notification, User
from app.views import get_user_from_token

bp_notifications = Blueprint("notifications", __name__, url_prefix="/api/notifications")

# TEST


def send_email(to_email, subject, body):
    """Send email with rate limiting"""
    # Rate limiting: 1 second delay between emails
    if not current_app.config.get("TESTING"):
        time.sleep(1)

    try:
        smtp_host = current_app.config.get("MAILTRAP_SMTP_HOST")
        smtp_port = current_app.config.get("MAILTRAP_SMTP_PORT")
        smtp_user = current_app.config.get("MAILTRAP_SMTP_USER")
        smtp_pass = current_app.config.get("MAILTRAP_SMTP_PASS")
        from_email = current_app.config.get("MAILTRAP_FROM_EMAIL")

        if not smtp_user or not smtp_pass:
            print(f"[MOCK EMAIL] To: {to_email}, Subject: {subject}")
            print(f"[MOCK EMAIL] Body: {body[:200]}...")
            return True

        print(f"[EMAIL] Attempting to send to {to_email} via {smtp_host}:{smtp_port}")

        msg = MIMEMultipart()
        msg["From"] = from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()

        print(f"[EMAIL] Successfully sent to {to_email}")
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email: {e}")
        return False


def email_notification(UserID, notification_type):
    # email_notification(User, Admire, notification_type):
    link = current_app.config.get("FRONTEND_URL", "http://localhost:5173")
    heading_noti = {
        "like": "You have a secret admire.",
        "match": "You have a new match.",
        "matching": "We might have found someone you might like.",
        "message": "You have a new message.",
    }
    body_noti = {
        "like": "You have a new secret admire. Come and find out who👀👀👀. 👉" + link,
        "match": "You have a new match. Come and find out who👀👀👀. 👉" + link,
        "matching": "We might have found someone you might like. Come and find out who👀👀👀. 👉"
        + link,
        "message": "Someone messaged you. Come and find out who👀👀👀. 👉" + link,
    }
    # get email from database
    # to_email=
    to_email = db.session.query(User.email).filter(User.user_id == UserID).scalar()

    heading = heading_noti.get(notification_type, "You have a new notification")
    body = body_noti.get(notification_type, "Check your notifications")
    send_email(to_email, heading, body)


# def notification ():
#     mail = mt.Mail(
#         sender=mt.Address(email="hello@demomailtrap.co", name="Mailtrap Test"),
#         to=[mt.Address(email="atraill1000@gmail.com")],
#         subject="You are awesome!",
#         text="Congrats for sending test email with Mailtrap!",
#         category="Integration Test",
#     )

#     client = mt.MailtrapClient(token="<YOUR_API_TOKEN>")
#     response = client.send(mail)

#     print(response)

#     name = form.name.data
#     email = form.email.data
#     subject = form.subject.data
#     message = form.message.data

#     msg = Message(subject, sender=(name, email), recipients=["sandbox.smtp.mailtrap.io"])
#     msg.body = message
#     # It naa work!!!!
#     mail.send(msg)
#     flash('The email was sucessfull sent.')
#     pass

# def matching_sys():
#     if age <=preferred_age_min and age>=preferred_age_max:
#         like +=1
#     for partner_interest in interests:
#         for myintrest in myintrest:
#             if partner_interest==myintrest:
#                 like+=1
#     if partner_gender == gender_preference:
#         like +=1
#     if partner_relationship_goal ==relationship_goal:
#         like +=1

#     like_pre = like/(len(intrest)+3)*100
#     return like_pre
# Test


# IN APP Notifications
@bp_notifications.route("", methods=["GET"])
def get_notifications():
    """Get notifications for current user."""
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    notifications = (
        Notification.query.filter_by(user_id=user.user_id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )

    # Add from_user profile info
    result = []
    for n in notifications:
        data = n.to_dict()
        if n.from_user_id:
            from_profile = (
                db.session.query(__import__("app.models", fromlist=["Profile"]).Profile)
                .filter_by(user_id=n.from_user_id)
                .first()
            )
            if from_profile:
                data["from_profile"] = from_profile.to_dict()
        result.append(data)

    return jsonify(result), 200


@bp_notifications.route("/unread-count", methods=["GET"])
def get_unread_count():
    """Get count of unread notifications."""
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    count = Notification.query.filter_by(user_id=user.user_id, is_read=False).count()

    return jsonify({"unread_count": count}), 200


@bp_notifications.route("/<int:notification_id>/read", methods=["PUT"])
def mark_as_read(notification_id):
    """Mark a notification as read."""
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    notification = Notification.query.filter_by(
        notification_id=notification_id, user_id=user.user_id
    ).first()

    if not notification:
        return jsonify({"error": "Notification not found"}), 404

    notification.is_read = True
    db.session.commit()

    return jsonify({"message": "Notification marked as read"}), 200


@bp_notifications.route("/read-all", methods=["PUT"])
def mark_all_as_read():
    """Mark all notifications as read."""
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    Notification.query.filter_by(user_id=user.user_id, is_read=False).update(
        {"is_read": True}
    )
    db.session.commit()

    return jsonify({"message": "All notifications marked as read"}), 200

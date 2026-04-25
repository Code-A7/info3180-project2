from flask import Blueprint, request, jsonify
from app import db
from app.models import Message, Match, Profile
from app.views import get_user_from_token
from app.matches import create_notification
from app.notifications import email_notification, send_email

bp_messages = Blueprint('messages', __name__, url_prefix='/api/messages')

MAX_MESSAGE_LENGTH = 1000
MAX_MESSAGES_PER_CONVERSATION = 200
MESSAGE_RETENTION_DAYS = 90


def check_match_exists(user1_id, user2_id):
    """Check if two users have a mutual match."""
    match = Match.query.filter(
        ((Match.user1_id == user1_id) & (Match.user2_id == user2_id)) |
        ((Match.user1_id == user2_id) & (Match.user2_id == user1_id))
    ).first()
    return match is not None


def get_socket_emit():
    from app import socketio
    from flask import current_app
    
    def emit(user_id, event, data):
        socketio.emit(event, data, room=f'user_{user_id}')
    
    return emit


@bp_messages.route('', methods=['GET'])
def get_conversations():
    """Get list of all conversations for current user."""
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get all unique users the current user has exchanged messages with
    sent_to = db.session.query(Message.receiver_id).filter(
        Message.sender_id == user.uid
    ).distinct()
    
    received_from = db.session.query(Message.sender_id).filter(
        Message.receiver_id == user.uid
    ).distinct()
    
    user_ids = set([r[0] for r in sent_to] + [r[0] for r in received_from])
    
    conversations = []
    for other_user_id in user_ids:
        # Check if they still have a match
        if not check_match_exists(user.uid, other_user_id):
            continue
        
        # Get profile
        profile = Profile.query.filter_by(user_id=other_user_id).first()
        if not profile:
            continue
        
        # Get last message
        last_message = Message.query.filter(
            ((Message.sender_id == user.uid) & (Message.receiver_id == other_user_id)) |
            ((Message.sender_id == other_user_id) & (Message.receiver_id == user.uid))
        ).order_by(Message.created_at.desc()).first()
        
        # Get unread count
        unread_count = Message.query.filter(
            Message.sender_id == other_user_id,
            Message.receiver_id == user.uid,
            Message.read_at == None
        ).count()
        
        conversations.append({
            'user_id': other_user_id,
            'user_name': profile.name,
            'profile_picture': profile.profile_picture,
            'last_message': last_message.content if last_message else '',
            'last_message_at': last_message.created_at.isoformat() if last_message and last_message.created_at else None,
            'unread_count': unread_count
        })
    
    # Sort by last message time
    conversations.sort(key=lambda x: x['last_message_at'] or '', reverse=True)
    
    return jsonify(conversations), 200


@bp_messages.route('/<int:other_user_id>', methods=['GET'])
def get_message_history(other_user_id):
    """Get message history with a specific user."""
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Check if matched
    if not check_match_exists(user.uid, other_user_id):
        return jsonify({'error': 'You can only message your matches'}), 403
    
    # Get messages (paginated)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    messages = Message.query.filter(
        ((Message.sender_id == user.uid) & (Message.receiver_id == other_user_id)) |
        ((Message.sender_id == other_user_id) & (Message.receiver_id == user.uid))
    ).order_by(Message.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Mark messages as read
    Message.query.filter(
        Message.sender_id == other_user_id,
        Message.receiver_id == user.uid,
        Message.read_at == None
    ).update({'read_at': db.func.now()})
    db.session.commit()
    
    # Get profile info
    profile = Profile.query.filter_by(user_id=other_user_id).first()
    
    return jsonify({
        'messages': [m.to_dict_extended(user.uid) for m in messages.items],
        'has_next': messages.has_next,
        'has_prev': messages.has_prev,
        'page': page,
        'total_pages': messages.pages,
        'other_user': profile.to_dict() if profile else None
    }), 200


@bp_messages.route('/<int:other_user_id>', methods=['POST'])
def send_message(other_user_id):
    """Send a message to a user."""
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Check if matched
    if not check_match_exists(user.uid, other_user_id):
        return jsonify({'error': 'You can only message your matches'}), 403
    
    data = request.get_json()
    content = data.get('content', '').strip()
    
    # Validate message length
    if not content:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    if len(content) > MAX_MESSAGE_LENGTH:
        return jsonify({'error': f'Message cannot exceed {MAX_MESSAGE_LENGTH} characters'}), 400
    
    # Create message
    message = Message(
        sender_id=user.uid,
        receiver_id=other_user_id,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    
    # Added TO Email
    create_notification(other_user_id, "message")

    
    # Emit WebSocket event
    try:
        emit = get_socket_emit()
        emit(other_user_id, 'new_message', {
            'sender_id': user.uid,
            'sender_name': Profile.query.filter_by(user_id=user.uid).first().name if Profile.query.filter_by(user_id=user.uid).first() else 'Unknown',
            'content': content,
            'created_at': message.created_at.isoformat()
        })
        
    except Exception as e:
        print(f"WebSocket emit error: {e}")
    
    return jsonify(message.to_dict_extended(user.uid)), 201


@bp_messages.route('/<int:message_id>/read', methods=['PUT'])
def mark_message_read(message_id):
    """Mark a message as read."""
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    message = Message.query.filter_by(id=message_id, receiver_id=user.uid).first()
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    
    message.read_at = db.func.now()
    db.session.commit()
    
    # Notify sender
    try:
        emit = get_socket_emit()
        emit(message.sender_id, 'message_read', {
            'message_id': message.id,
            'read_at': message.read_at.isoformat() if message.read_at else None
        })
    except Exception as e:
        print(f"WebSocket emit error: {e}")
    
    return jsonify({'message': 'Message marked as read'}), 200


@bp_messages.route('/unread', methods=['GET'])
def get_unread_count():
    """Get total unread message count."""
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    count = Message.query.filter(
        Message.receiver_id == user.uid,
        Message.read_at == None
    ).count()
    
    return jsonify({'unread_count': count}), 200


@bp_messages.route('/typing/<int:other_user_id>', methods=['POST'])
def send_typing_status(other_user_id):
    """Send typing status to a user."""
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Check if matched
    if not check_match_exists(user.uid, other_user_id):
        return jsonify({'error': 'You can only message your matches'}), 403
    
    data = request.get_json()
    is_typing = data.get('is_typing', False)
    
    # Get sender name
    profile = Profile.query.filter_by(user_id=user.uid).first()
    sender_name = profile.name if profile else 'Unknown'
    
    # Emit typing status
    try:
        emit = get_socket_emit()
        emit(other_user_id, 'user_typing', {
            'user_id': user.uid,
            'user_name': sender_name,
            'is_typing': is_typing
        })
    except Exception as e:
        print(f"WebSocket emit error: {e}")
    
    return jsonify({'message': 'Typing status sent'}), 200


@bp_messages.route('/cleanup', methods=['POST'])
def cleanup_old_messages():
    """Clean up old messages (admin endpoint)."""
    user = get_user_from_token()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    from datetime import timedelta
    from datetime import datetime, timezone
    
    cutoff = datetime.now(timezone.utc) - timedelta(days=MESSAGE_RETENTION_DAYS)
    
    deleted = Message.query.filter(Message.created_at < cutoff).delete()
    db.session.commit()
    
    return jsonify({
        'message': f'Cleaned up {deleted} messages',
        'deleted_count': deleted
    }), 200

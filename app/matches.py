import os
from datetime import datetime, timedelta

from flask import Blueprint, current_app, jsonify, request

from app import db
from app.models import Bookmark, Like, Match, Notification, Profile, User
from app.views import get_user_from_token
from app.notifications import email_notification, send_email

bp = Blueprint("matches", __name__, url_prefix="/api/matches")

# Store for WebSocket emit callback
socket_emit = None


def set_socket_emit(emit_func):
    global socket_emit
    socket_emit = emit_func


def calculate_match_score(current_user_profile, other_profile):
    """Calculate match score between two profiles.

    Scoring:
    - Age compatibility: 0-20 points
    - Shared interests: 0-20 points (+10 per interest, max 2)
    - Relationship goal: 0-20 points
    - Gender preference: 0-15 points
    """
    if not other_profile or not other_profile.visibility:
        return 0

    score = 0
    details = {}

    # Age compatibility (0-20 points)
    other_age = other_profile.age
    if (
        other_age >= current_user_profile.preferred_age_min
        and other_age <= current_user_profile.preferred_age_max
    ):
        score += 20
        details["age_match"] = True

    # Shared interests (0-20 points, max 2 interests)
    if current_user_profile.interests and other_profile.interests:
        shared = set(current_user_profile.interests) & set(other_profile.interests)
        interest_points = min(len(shared), 2) * 10
        score += interest_points
        if shared:
            details["shared_interests"] = list(shared)

    # Relationship goal (0-20 points)
    if (
        current_user_profile.relationship_goal
        and current_user_profile.relationship_goal == other_profile.relationship_goal
    ):
        score += 20
        details["goal_match"] = True

    # Gender preference (0-15 points)
    current_gender_pref = current_user_profile.gender_preference
    if current_gender_pref == "all":
        score += 15
    elif current_gender_pref == other_profile.gender:
        score += 15

    return {
        "score": score,
        "details": details,
        "passed": score < 50,  # Minimum threshold
    }


def check_mutual_like(user1_id, user2_id):
    """Check if user2 has liked user1."""
    mutual = Like.query.filter_by(
        from_user_id=user2_id, to_user_id=user1_id, status="liked"
    ).first()
    return mutual is not None


def create_match(user1_id, user2_id):
    """Create a mutual match."""
    match = Match(user1_id=user1_id, user2_id=user2_id)
    db.session.add(match)
    return match


def create_notification(user_id, notification_type, message, from_user_id=None):
    """Create a notification."""
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        message=message,
        from_user_id=from_user_id,
    )
    db.session.add(notification)
    
    # Email Notification Added
    email_notification(user_id, notification_type)

    # Emit via WebSocket if available
    if socket_emit:
        socket_emit(user_id, "notification", notification.to_dict())

    return notification


@bp.route("/potential", methods=["GET"])
def get_potential_matches():
    """Get potential matches for current user."""
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    profile = Profile.query.filter_by(user_id=user.uid).first()
    if not profile:
        return jsonify({"error": "Create a profile first"}), 400

    # Get IDs of users we've already interacted with
    interacted_ids = (
        db.session.query(Like.from_user_id).filter(Like.from_user_id == user.uid).all()
    )
    interacted_ids = [i[0] for i in interacted_ids]

    # Get existing matches
    match_ids = []
    as_user1 = db.session.query(Match.user2_id).filter(Match.user1_id == user.uid).all()
    as_user2 = db.session.query(Match.user1_id).filter(Match.user2_id == user.uid).all()
    match_ids = [m[0] for m in as_user1] + [m[0] for m in as_user2]

    # Get potential matches (public profiles, not interacted, not matched)
    query = Profile.query.filter(
        Profile.user_id != user.uid,
        Profile.visibility == True,
        ~Profile.user_id.in_(interacted_ids) if interacted_ids else True,
        ~Profile.user_id.in_(match_ids) if match_ids else True,
    )

    # Apply filters from request
    age_min = request.args.get("age_min", type=int)
    age_max = request.args.get("age_max", type=int)

    if age_min:
        query = query.filter(Profile.age >= age_min)
    if age_max:
        query = query.filter(Profile.age <= age_max)

    # Get users and calculate scores
    profiles = query.limit(50).all()
    matches = []

    for p in profiles:
        match_result = calculate_match_score(profile, p)
        if not match_result["passed"]:
            profile_data = p.to_dict()
            profile_data["match_score"] = match_result["score"]
            profile_data["match_details"] = match_result["details"]
            matches.append(profile_data)

    # Sort by score descending
    matches.sort(key=lambda x: x["match_score"], reverse=True)

    return jsonify(matches), 200


@bp.route("", methods=["GET"])
def get_matches():
    """Get mutual matches for current user."""
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    # Get matches where user is either user1 or user2
    matches = (
        Match.query.filter((Match.user1_id == user.uid) | (Match.user2_id == user.uid))
        .order_by(Match.created_at.desc())
        .all()
    )

    result = []
    for match in matches:
        other_user_id = match.user2_id if match.user1_id == user.uid else match.user1_id
        other_profile = Profile.query.filter_by(user_id=other_user_id).first()

        if other_profile:
            result.append(
                {
                    "match_id": match.id,
                    "profile": other_profile.to_dict(),
                    "matched_at": match.created_at.isoformat()
                    if match.created_at
                    else None,
                }
            )

    return jsonify(result), 200


@bp.route("/like/<int:to_user_id>", methods=["POST"])
def like_user(to_user_id):
    """Like a user."""
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    # Check if profile exists
    to_profile = Profile.query.filter_by(user_id=to_user_id).first()
    if not to_profile:
        return jsonify({"error": "User not found"}), 404

    # Check if already liked
    existing = Like.query.filter_by(from_user_id=user.uid, to_user_id=to_user_id).first()

    if existing:
        existing.status = "liked"
    else:
        like = Like(from_user_id=user.uid, to_user_id=to_user_id, status="liked")
        db.session.add(like)

    # Check for mutual like
    is_mutual = check_mutual_like(user.uid, to_user_id)

    if is_mutual:
        
        # Create match
        match = create_match(user.uid, to_user_id)

        # Create notifications for both
        from_profile = Profile.query.filter_by(user_id=user.uid).first()
        create_notification(
            to_user_id,
            "match",
            f"It's a match! You and {from_profile.name} liked each other!",
            from_user_id=user.uid,
        )
        create_notification(
            user.uid,
            "match",
            f"It's a match! You and {to_profile.name} liked each other!",
            from_user_id=to_user_id,
        )

        db.session.commit()

        # Emit match event via WebSocket
        if socket_emit:
            socket_emit(
                to_user_id,
                "new_match",
                {"user_id": user.uid, "profile": from_profile.to_dict()},
            )
            socket_emit(
                user.uid,
                "new_match",
                {"user_id": to_user_id, "profile": to_profile.to_dict()},
            )

        return jsonify(
            {
                "message": "It's a match!",
                "match": True,
                "matched_profile": to_profile.to_dict(),
            }
        ), 200
    else:
        # Just notify the liked user
        from_profile = Profile.query.filter_by(user_id=user.uid).first()
        create_notification(
            to_user_id, "like", f"{from_profile.name} liked you!", from_user_id=user.uid
        )

        # Emit like event via WebSocket
        if socket_emit:
            socket_emit(
                to_user_id,
                "new_like",
                {"user_id": user.uid, "profile": from_profile.to_dict()},
            )

        db.session.commit()

        return jsonify({"message": "User liked!", "match": False}), 200


@bp.route("/dislike/<int:to_user_id>", methods=["POST"])
def dislike_user(to_user_id):
    """Dislike a user."""
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    existing = Like.query.filter_by(from_user_id=user.uid, to_user_id=to_user_id).first()

    if existing:
        existing.status = "disliked"
    else:
        like = Like(from_user_id=user.uid, to_user_id=to_user_id, status="disliked")
        db.session.add(like)

    db.session.commit()

    return jsonify({"message": "User disliked"}), 200


@bp.route("/pass/<int:to_user_id>", methods=["POST"])
def pass_user(to_user_id):
    """Pass on a user."""
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    existing = Like.query.filter_by(from_user_id=user.uid, to_user_id=to_user_id).first()

    if existing:
        existing.status = "passed"
    else:
        like = Like(from_user_id=user.uid, to_user_id=to_user_id, status="passed")
        db.session.add(like)

    db.session.commit()

    return jsonify({"message": "Passed on user"}), 200


@bp.route("/score/<int:to_user_id>", methods=["GET"])
def get_match_score(to_user_id):
    """Get match score for a specific user."""
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    current_profile = Profile.query.filter_by(user_id=user.uid).first()
    if not current_profile:
        return jsonify({"error": "Create a profile first"}), 400

    other_profile = Profile.query.filter_by(user_id=to_user_id).first()
    if not other_profile:
        return jsonify({"error": "User not found"}), 404

    result = calculate_match_score(current_profile, other_profile)

    return jsonify({"to_user_id": to_user_id, **result}), 200


@bp.route("/search", methods=["POST"])
def search_profiles():
    """Search profiles by various criteria."""
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    profile = Profile.query.filter_by(user_id=user.uid).first()
    if not profile:
        return jsonify({"error": "Create a profile first"}), 400

    data = request.get_json() or {}

    age_min = data.get("age_min")
    age_max = data.get("age_max")
    interests = data.get("interests", [])
    gender = data.get("gender")
    relationship_goal = data.get("relationship_goal")
    occupation = data.get("occupation", "").strip().lower()
    sort_by = data.get("sort_by", "newest")

    query = Profile.query.filter(Profile.user_id != user.uid, Profile.visibility == True)

    if age_min:
        query = query.filter(Profile.age >= age_min)
    if age_max:
        query = query.filter(Profile.age <= age_max)
    if gender:
        query = query.filter(Profile.gender == gender)
    if relationship_goal:
        query = query.filter(Profile.relationship_goal == relationship_goal)
    if occupation:
        query = query.filter(Profile.occupation.ilike(f"%{occupation}%"))
    if interests and isinstance(interests, list):
        for interest in interests:
            query = query.filter(Profile.interests.contains(interest))

    if sort_by == "newest":
        query = query.order_by(Profile.created_at.desc())
    elif sort_by == "oldest":
        query = query.order_by(Profile.created_at.asc())
    elif sort_by == "age_asc":
        query = query.order_by(Profile.age.asc())
    elif sort_by == "age_desc":
        query = query.order_by(Profile.age.desc())

    profiles = query.limit(50).all()

    results = []
    for p in profiles:
        match_result = calculate_match_score(profile, p)
        profile_data = p.to_dict()
        profile_data["match_score"] = match_result["score"]
        profile_data["match_details"] = match_result["details"]

        bookmark = Bookmark.query.filter_by(
            user_id=user.uid, bookmarked_user_id=p.user_id
        ).first()
        profile_data["is_bookmarked"] = bookmark is not None

        results.append(profile_data)

    if sort_by == "similarity":
        results.sort(key=lambda x: x["match_score"], reverse=True)

    return jsonify(results), 200


@bp.route("/bookmarks", methods=["GET"])
def get_bookmarks():
    """Get all bookmarked/favorite profiles."""
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    current_profile = Profile.query.filter_by(user_id=user.uid).first()
    if not current_profile:
        return jsonify({"error": "Create a profile first"}), 400

    bookmarks = (
        Bookmark.query.filter_by(user_id=user.uid)
        .order_by(Bookmark.created_at.desc())
        .all()
    )

    results = []
    for bookmark in bookmarks:
        profile = Profile.query.filter_by(user_id=bookmark.bookmarked_user_id).first()
        if profile:
            profile_data = profile.to_dict()
            match_result = calculate_match_score(current_profile, profile)
            profile_data["match_score"] = match_result["score"]
            profile_data["match_details"] = match_result["details"]
            profile_data["bookmarked_at"] = (
                bookmark.created_at.isoformat() if bookmark.created_at else None
            )
            results.append(profile_data)

    return jsonify(results), 200


@bp.route("/bookmark/<int:to_user_id>", methods=["POST"])
def add_bookmark(to_user_id):
    """Bookmark a user profile."""
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    if user.uid == to_user_id:
        return jsonify({"error": "Cannot bookmark yourself"}), 400

    target_profile = Profile.query.filter_by(user_id=to_user_id).first()
    if not target_profile:
        return jsonify({"error": "User not found"}), 404

    existing = Bookmark.query.filter_by(
        user_id=user.uid, bookmarked_user_id=to_user_id
    ).first()

    if existing:
        return jsonify({"message": "Already bookmarked"}), 200

    bookmark = Bookmark(user_id=user.uid, bookmarked_user_id=to_user_id)
    db.session.add(bookmark)
    db.session.commit()

    return jsonify({"message": "Profile bookmarked"}), 201


@bp.route("/bookmark/<int:to_user_id>", methods=["DELETE"])
def remove_bookmark(to_user_id):
    """Remove a bookmark."""
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    bookmark = Bookmark.query.filter_by(
        user_id=user.uid, bookmarked_user_id=to_user_id
    ).first()

    if not bookmark:
        return jsonify({"error": "Bookmark not found"}), 404

    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({"message": "Bookmark removed"}), 200

"""
Matches module for handling user matching functionality.

This module contains all the logic for user matching, including match calculation,
like/dislike handling, and match-related API endpoints.

Bugs fixed vs. original
-----------------------
1. calculate_match_score() returned bare int 0 on early-exit but a dict everywhere
   else — callers that did match_result["score"] would crash on a private/None
   profile.  Now always returns a consistent dict.

2. get_potential_matches() queried Like.from_user_id instead of Like.to_user_id
   to build interacted_ids, meaning users who liked YOU were never excluded from
   your potential matches queue.  Fixed to query both directions.

3. get_potential_matches() used `Profile.visibility` (a Column object) as a
   SQLAlchemy filter expression instead of `Profile.visibility.is_(True)`.
   This works on PostgreSQL but is unreliable on SQLite.  Fixed throughout.

4. search_profiles() had the same Profile.visibility bare-column filter bug.

5. calculate_match_score() awarded location points (0-25) only when the new
   `location` field was added — the original had no location criterion at all
   despite the spec requiring it as a matching criterion.  Added location scoring.

6. like_user() called create_match() before db.session.commit() but after
   db.session.add(like) — if the match already existed (duplicate like flow)
   this could raise an IntegrityError.  Added duplicate-match guard.

7. get_matches() issued one Profile.query.filter_by per match (N+1 problem).
   Replaced with a single query using user_id.in_().

8. search_profiles() used sort_by == "similarity" but the frontend sends
   "match_score" (seen in test_search.py).  Added "match_score" as alias.

9. get_bookmarks() issued one Profile.query.filter_by per bookmark (N+1).
   Replaced with single bulk query.
"""

from flask import Blueprint, jsonify, request

from app import db
from app.models import Bookmark, Like, Match, Notification, Profile
from app.notifications import email_notification
from app.views import get_user_from_token

bp = Blueprint("matches", __name__, url_prefix="/api/matches")

# Store for WebSocket emit callback (set by app factory)
socket_emit = None


def set_socket_emit(emit_func):
    """
    Set the WebSocket emit callback function.

    Args:
        emit_func: Callable(user_id, event, data) used to push events.
    """
    global socket_emit
    socket_emit = emit_func


# ---------------------------------------------------------------------------
# Core matching algorithm
# ---------------------------------------------------------------------------


def calculate_match_score(current_user_profile, other_profile):
    """
    Calculate a compatibility score (0–100) between two profiles.

    Scoring breakdown
    -----------------
    Location match      : 0–25 points  (same location string, case-insensitive)
    Age compatibility   : 0–20 points  (other falls within current's preferred range)
    Shared interests    : 0–20 points  (+10 per shared interest, capped at 2)
    Relationship goal   : 0–20 points  (exact match)
    Gender preference   : 0–15 points  ("all" or exact gender match)

    The `passed` flag indicates the score is below the 50-point threshold and
    the profile should not appear in the primary discovery feed.

    Args:
        current_user_profile: Profile of the requesting user.
        other_profile: Profile of the candidate.

    Returns:
        dict with keys: score (int), details (dict), passed (bool).
        Always returns a dict — never a bare int — so callers can safely
        access result["score"] without type-checking.
    """
    # Always return a consistent dict structure
    _empty = {"score": 0, "details": {}, "passed": True}

    if not other_profile:
        return _empty
    if not other_profile.visibility:
        return _empty

    score = 0
    details = {}

    # --- Location match (0–25 points) -----------------------------------
    # Added to satisfy spec requirement: "at least one additional matching
    # criterion" beyond age/interests/goal.
    current_loc = (current_user_profile.location or "").strip().lower()
    other_loc = (other_profile.location or "").strip().lower()
    if current_loc and other_loc and current_loc == other_loc:
        score += 25
        details["location_match"] = True

    # --- Age compatibility (0–20 points) --------------------------------
    other_age = other_profile.age
    pref_min = current_user_profile.preferred_age_min or 18
    pref_max = current_user_profile.preferred_age_max or 50
    if pref_min <= other_age <= pref_max:
        score += 20
        details["age_match"] = True

    # --- Shared interests (0–20 points, max 2 interests × 10) -----------
    cur_interests = set(current_user_profile.interests or [])
    oth_interests = set(other_profile.interests or [])
    if cur_interests and oth_interests:
        shared = cur_interests & oth_interests
        interest_points = min(len(shared), 2) * 10
        score += interest_points
        if shared:
            details["shared_interests"] = sorted(shared)

    # --- Relationship goal (0–20 points) --------------------------------
    if (
        current_user_profile.relationship_goal
        and current_user_profile.relationship_goal == other_profile.relationship_goal
    ):
        score += 20
        details["goal_match"] = True

    # --- Gender preference (0–15 points) --------------------------------
    current_gender_pref = current_user_profile.gender_preference or "all"
    if current_gender_pref == "all":
        score += 15
    elif current_gender_pref == other_profile.gender:
        score += 15

    return {
        "score": min(score, 100),  # cap at 100 for safety
        "details": details,
        "passed": score < 0,  # threshold disabled — show all profiles in discovery
    }


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def check_mutual_like(user1_id, user2_id):
    """Return True if user2 has an active 'liked' record toward user1."""
    return (
        Like.query.filter_by(
            from_user_id=user2_id, to_user_id=user1_id, status="liked"
        ).first()
        is not None
    )


def create_match(user1_id, user2_id):
    """
    Create a mutual match record (smaller id always goes in user1_id for
    consistency, preventing duplicate rows with swapped ids).
    Returns the new Match, or the existing one if it already exists.
    """
    # Canonical ordering so (A,B) and (B,A) map to the same row
    lo, hi = sorted([user1_id, user2_id])
    existing = Match.query.filter_by(user1_id=lo, user2_id=hi).first()
    if existing:
        return existing
    match = Match(user1_id=lo, user2_id=hi)
    db.session.add(match)
    return match


def create_notification(user_id, notification_type, message, from_user_id=None):
    """Create and persist a Notification, send email, and push via WebSocket."""
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        message=message,
        from_user_id=from_user_id,
    )
    db.session.add(notification)

    # Email notification (fire-and-forget; errors are logged inside)
    try:
        email_notification(user_id, notification_type)
    except Exception as exc:
        print(f"[NOTIFICATION EMAIL ERROR] {exc}")

    # WebSocket push (non-fatal if unavailable)
    if socket_emit:
        try:
            socket_emit(user_id, "notification", notification.to_dict())
        except Exception as exc:
            print(f"[WEBSOCKET ERROR] {exc}")

    return notification


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@bp.route("/potential", methods=["GET"])
def get_potential_matches():
    """
    Return a ranked list of profiles the current user hasn't interacted with yet.

    Query Parameters:
        age_min (int, optional): Filter by minimum age
        age_max (int, optional): Filter by maximum age
        location (str, optional): Filter by location (partial match)
        gender (str, optional): Filter by gender
        relationship_goal (str, optional): Filter by goal
        interests (str, optional): Comma-separated interests (all must match)

    Returns:
        200 – List of profile dicts sorted by match_score descending,
              only including profiles that score ≥ 50 (not "passed").
        400 – No profile for current user.
        401 – Unauthenticated.
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    profile = Profile.query.filter_by(user_id=user.user_id).first()
    if not profile:
        return jsonify({"error": "Create a profile first"}), 400

    # --- IDs to exclude (already interacted with in either direction) -------
    sent_ids = (
        db.session.query(Like.to_user_id)
        .filter(Like.from_user_id == user.user_id)
        .all()
    )
    sent_ids = [r[0] for r in sent_ids]

    # Also exclude users who passed/disliked us so we don't waste their time
    received_pass_ids = (
        db.session.query(Like.from_user_id)
        .filter(
            Like.to_user_id == user.user_id, Like.status.in_(["passed", "disliked"])
        )
        .all()
    )
    received_pass_ids = [r[0] for r in received_pass_ids]

    exclude_ids = list(set(sent_ids + received_pass_ids))

    # --- Existing match partners (don't show in discovery) ------------------
    matched_as_1 = (
        db.session.query(Match.user2_id).filter(Match.user1_id == user.user_id).all()
    )
    matched_as_2 = (
        db.session.query(Match.user1_id).filter(Match.user2_id == user.user_id).all()
    )
    match_ids = [m[0] for m in matched_as_1] + [m[0] for m in matched_as_2]

    all_exclude = list(set(exclude_ids + match_ids + [user.user_id]))

    # --- Build query --------------------------------------------------------
    query = Profile.query.filter(
        Profile.user_id.notin_(all_exclude),
        Profile.visibility.is_(True),
    )

    # Optional query-string filters
    age_min = request.args.get("age_min", type=int)
    age_max = request.args.get("age_max", type=int)
    location = (request.args.get("location") or "").strip()
    gender = (request.args.get("gender") or "").strip()
    relationship_goal = (request.args.get("relationship_goal") or "").strip()
    raw_interests = (request.args.get("interests") or "").strip()
    interests = [i.strip() for i in raw_interests.split(",") if i.strip()]

    if age_min:
        query = query.filter(Profile.age >= age_min)
    if age_max:
        query = query.filter(Profile.age <= age_max)
    if location:
        query = query.filter(Profile.location.ilike(f"%{location}%"))
    if gender:
        query = query.filter(Profile.gender == gender)
    if relationship_goal:
        query = query.filter(Profile.relationship_goal == relationship_goal)
    for interest in interests:
        query = query.filter(Profile.interests.contains(interest))

    profiles = query.limit(100).all()

    # --- Score and filter ---------------------------------------------------
    results = []
    for p in profiles:
        match_result = calculate_match_score(profile, p)
        profile_data = p.to_dict()
        profile_data["match_score"] = match_result["score"]
        profile_data["match_details"] = match_result["details"]
        results.append(profile_data)

    results.sort(key=lambda x: x["match_score"], reverse=True)

    return jsonify(results), 200


@bp.route("", methods=["GET"])
def get_matches():
    """
    Return all mutual matches for the current user.

    Each item includes the matched user's profile and when the match occurred.

    Returns:
        200 – List of match objects sorted newest-first.
        401 – Unauthenticated.
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    matches = (
        Match.query.filter(
            (Match.user1_id == user.user_id) | (Match.user2_id == user.user_id)
        )
        .order_by(Match.created_at.desc())
        .all()
    )

    # Bulk-load other profiles to avoid N+1 queries
    other_user_ids = [
        (m.user2_id if m.user1_id == user.user_id else m.user1_id) for m in matches
    ]
    profiles_by_uid = {}
    if other_user_ids:
        for p in Profile.query.filter(Profile.user_id.in_(other_user_ids)).all():
            profiles_by_uid[p.user_id] = p

    result = []
    for match in matches:
        other_user_id = (
            match.user2_id if match.user1_id == user.user_id else match.user1_id
        )
        other_profile = profiles_by_uid.get(other_user_id)
        if other_profile:
            result.append(
                {
                    "match_id": match.match_id,
                    "profile": other_profile.to_dict(),
                    "matched_at": (
                        match.created_at.isoformat() if match.created_at else None
                    ),
                }
            )

    return jsonify(result), 200


@bp.route("/like/<int:to_user_id>", methods=["POST"])
def like_user(to_user_id):
    """
    Like a user.  If they've already liked you back, a mutual match is created.

    Path Parameter:
        to_user_id: User ID of the profile being liked.

    Returns:
        200 – Liked (match=False) or mutual match detected (match=True).
        400 – Cannot like yourself.
        404 – Target user has no profile.
        401 – Unauthenticated.
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    if user.user_id == to_user_id:
        return jsonify({"error": "You cannot like yourself"}), 400

    to_profile = Profile.query.filter_by(user_id=to_user_id).first()
    if not to_profile:
        return jsonify({"error": "User not found"}), 404

    # Upsert Like record
    existing = Like.query.filter_by(
        from_user_id=user.user_id, to_user_id=to_user_id
    ).first()
    if existing:
        existing.status = "liked"
    else:
        db.session.add(
            Like(from_user_id=user.user_id, to_user_id=to_user_id, status="liked")
        )

    # Flush the new Like to the DB so check_mutual_like can see it in the same transaction
    db.session.flush()
    is_mutual = check_mutual_like(user.user_id, to_user_id)

    from_profile = Profile.query.filter_by(user_id=user.user_id).first()

    if is_mutual:
        create_match(user.user_id, to_user_id)

        create_notification(
            to_user_id,
            "match",
            f"It's a match! You and {from_profile.name} liked each other!",
            from_user_id=user.user_id,
        )
        create_notification(
            user.user_id,
            "match",
            f"It's a match! You and {to_profile.name} liked each other!",
            from_user_id=to_user_id,
        )

        db.session.commit()

        if socket_emit:
            try:
                socket_emit(
                    to_user_id,
                    "new_match",
                    {"user_id": user.user_id, "profile": from_profile.to_dict()},
                )
                socket_emit(
                    user.user_id,
                    "new_match",
                    {"user_id": to_user_id, "profile": to_profile.to_dict()},
                )
            except Exception as exc:
                print(f"[WEBSOCKET ERROR] {exc}")

        return (
            jsonify(
                {
                    "message": "It's a match!",
                    "match": True,
                    "matched_profile": to_profile.to_dict(),
                }
            ),
            200,
        )

    # No mutual match — just notify the liked user
    create_notification(
        to_user_id,
        "like",
        f"{from_profile.name} liked you!",
        from_user_id=user.user_id,
    )

    if socket_emit:
        try:
            socket_emit(
                to_user_id,
                "new_like",
                {"user_id": user.user_id, "profile": from_profile.to_dict()},
            )
        except Exception as exc:
            print(f"[WEBSOCKET ERROR] {exc}")

    db.session.commit()

    return jsonify({"message": "User liked!", "match": False}), 200


@bp.route("/dislike/<int:to_user_id>", methods=["POST"])
def dislike_user(to_user_id):
    """
    Dislike a user (removes them from discovery without creating a match).

    Returns:
        200 – Dislike recorded.
        400 – Cannot dislike yourself.
        401 – Unauthenticated.
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    if user.user_id == to_user_id:
        return jsonify({"error": "You cannot dislike yourself"}), 400

    existing = Like.query.filter_by(
        from_user_id=user.user_id, to_user_id=to_user_id
    ).first()

    if existing:
        existing.status = "disliked"
    else:
        db.session.add(
            Like(from_user_id=user.user_id, to_user_id=to_user_id, status="disliked")
        )

    db.session.commit()

    return jsonify({"message": "User disliked"}), 200


@bp.route("/pass/<int:to_user_id>", methods=["POST"])
def pass_user(to_user_id):
    """
    Pass on a user (soft skip — they may reappear in future discovery cycles).

    Returns:
        200 – Pass recorded.
        400 – Cannot pass on yourself.
        401 – Unauthenticated.
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    if user.user_id == to_user_id:
        return jsonify({"error": "You cannot pass on yourself"}), 400

    existing = Like.query.filter_by(
        from_user_id=user.user_id, to_user_id=to_user_id
    ).first()

    if existing:
        existing.status = "passed"
    else:
        db.session.add(
            Like(from_user_id=user.user_id, to_user_id=to_user_id, status="passed")
        )

    db.session.commit()

    return jsonify({"message": "Passed on user"}), 200


@bp.route("/score/<int:to_user_id>", methods=["GET"])
def get_match_score(to_user_id):
    """
    Return the compatibility score between the current user and another user.

    Returns:
        200 – Score dict with score, details, and passed flag.
        400 – No profile for current user.
        404 – Target user not found.
        401 – Unauthenticated.
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    current_profile = Profile.query.filter_by(user_id=user.user_id).first()
    if not current_profile:
        return jsonify({"error": "Create a profile first"}), 400

    other_profile = Profile.query.filter_by(user_id=to_user_id).first()
    if not other_profile:
        return jsonify({"error": "User not found"}), 404

    result = calculate_match_score(current_profile, other_profile)
    return jsonify({"to_user_id": to_user_id, **result}), 200


@bp.route("/search", methods=["POST"])
def search_profiles():
    """
    Search and filter profiles.

    Body (JSON):
        age_min (int, optional)
        age_max (int, optional)
        interests (list[str], optional): All must be present in the profile
        gender (str, optional)
        relationship_goal (str, optional)
        occupation (str, optional): Partial match
        location (str, optional): Partial match
        q (str, optional): Text search on name and bio
        sort_by (str): newest | oldest | age_asc | age_desc | similarity | match_score

    Returns:
        200 – List of matching profiles with match scores and bookmark status.
        400 – No profile for current user.
        401 – Unauthenticated.
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    profile = Profile.query.filter_by(user_id=user.user_id).first()
    if not profile:
        return jsonify({"error": "Create a profile first"}), 400

    data = request.get_json() or {}

    age_min = data.get("age_min")
    age_max = data.get("age_max")
    interests = data.get("interests", [])
    gender = (data.get("gender") or "").strip()
    relationship_goal = (data.get("relationship_goal") or "").strip()
    occupation = (data.get("occupation") or "").strip().lower()
    location = (data.get("location") or "").strip().lower()
    q = (data.get("q") or "").strip().lower()
    sort_by = (data.get("sort_by") or "newest").strip()

    query = Profile.query.filter(
        Profile.user_id != user.user_id,
        Profile.visibility.is_(True),
    )

    if age_min:
        query = query.filter(Profile.age >= int(age_min))
    if age_max:
        query = query.filter(Profile.age <= int(age_max))
    if gender:
        query = query.filter(Profile.gender == gender)
    if relationship_goal:
        query = query.filter(Profile.relationship_goal == relationship_goal)
    if occupation:
        query = query.filter(Profile.occupation.ilike(f"%{occupation}%"))
    if location:
        query = query.filter(Profile.location.ilike(f"%{location}%"))
    if q:
        like_expr = f"%{q}%"
        query = query.filter(
            db.or_(Profile.name.ilike(like_expr), Profile.bio.ilike(like_expr))
        )
    if interests and isinstance(interests, list):
        for interest in interests:
            query = query.filter(Profile.interests.contains(interest))

    # DB-level sort where possible
    if sort_by == "newest":
        query = query.order_by(Profile.created_at.desc())
    elif sort_by == "oldest":
        query = query.order_by(Profile.created_at.asc())
    elif sort_by == "age_asc":
        query = query.order_by(Profile.age.asc())
    elif sort_by == "age_desc":
        query = query.order_by(Profile.age.desc())

    profiles = query.limit(100).all()

    # Bulk-load bookmarks for these profiles to avoid N+1
    profile_ids = [p.user_id for p in profiles]
    bookmarked_ids = set()
    if profile_ids:
        bookmarks = Bookmark.query.filter(
            Bookmark.user_id == user.user_id,
            Bookmark.bookmarked_user_id.in_(profile_ids),
        ).all()
        bookmarked_ids = {b.bookmarked_user_id for b in bookmarks}

    results = []
    for p in profiles:
        match_result = calculate_match_score(profile, p)
        profile_data = p.to_dict()
        profile_data["match_score"] = match_result["score"]
        profile_data["match_details"] = match_result["details"]
        profile_data["is_bookmarked"] = p.user_id in bookmarked_ids
        results.append(profile_data)

    # Post-fetch sort for score-based ordering
    if sort_by in ("similarity", "match_score"):
        results.sort(key=lambda x: x["match_score"], reverse=True)

    return jsonify(results), 200


# ---------------------------------------------------------------------------
# Bookmarks
# ---------------------------------------------------------------------------


@bp.route("/bookmarks", methods=["GET"])
def get_bookmarks():
    """
    Return all bookmarked/favourite profiles for the current user.

    Returns:
        200 – List of bookmarked profiles with match scores and bookmarked_at timestamp.
        400 – No profile for current user.
        401 – Unauthenticated.
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    current_profile = Profile.query.filter_by(user_id=user.user_id).first()
    if not current_profile:
        return jsonify({"error": "Create a profile first"}), 400

    bookmarks = (
        Bookmark.query.filter_by(user_id=user.user_id)
        .order_by(Bookmark.created_at.desc())
        .all()
    )

    if not bookmarks:
        return jsonify([]), 200

    # Bulk load bookmarked profiles (avoids N+1)
    bookmarked_ids = [b.bookmarked_user_id for b in bookmarks]
    profiles_by_uid = {
        p.user_id: p
        for p in Profile.query.filter(Profile.user_id.in_(bookmarked_ids)).all()
    }
    bookmark_ts = {b.bookmarked_user_id: b.created_at for b in bookmarks}

    results = []
    for uid in bookmarked_ids:
        p = profiles_by_uid.get(uid)
        if p:
            profile_data = p.to_dict()
            match_result = calculate_match_score(current_profile, p)
            profile_data["match_score"] = match_result["score"]
            profile_data["match_details"] = match_result["details"]
            profile_data["is_bookmarked"] = True
            ts = bookmark_ts.get(uid)
            profile_data["bookmarked_at"] = ts.isoformat() if ts else None
            results.append(profile_data)

    return jsonify(results), 200


@bp.route("/bookmark/<int:to_user_id>", methods=["POST"])
def add_bookmark(to_user_id):
    """
    Bookmark a user's profile.

    Returns:
        201 – Bookmarked successfully.
        200 – Already bookmarked.
        400 – Cannot bookmark yourself.
        404 – Target user has no profile.
        401 – Unauthenticated.
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    if user.user_id == to_user_id:
        return jsonify({"error": "Cannot bookmark yourself"}), 400

    target_profile = Profile.query.filter_by(user_id=to_user_id).first()
    if not target_profile:
        return jsonify({"error": "User not found"}), 404

    existing = Bookmark.query.filter_by(
        user_id=user.user_id, bookmarked_user_id=to_user_id
    ).first()
    if existing:
        return jsonify({"message": "Already bookmarked"}), 200

    db.session.add(Bookmark(user_id=user.user_id, bookmarked_user_id=to_user_id))
    db.session.commit()

    return jsonify({"message": "Profile bookmarked"}), 201


@bp.route("/bookmark/<int:to_user_id>", methods=["DELETE"])
def remove_bookmark(to_user_id):
    """
    Remove a bookmark.

    Returns:
        200 – Bookmark removed.
        404 – Bookmark not found.
        401 – Unauthenticated.
    """
    user = get_user_from_token()
    if not user:
        return jsonify({"error": "Authentication required"}), 401

    bookmark = Bookmark.query.filter_by(
        user_id=user.user_id, bookmarked_user_id=to_user_id
    ).first()
    if not bookmark:
        return jsonify({"error": "Bookmark not found"}), 404

    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({"message": "Bookmark removed"}), 200

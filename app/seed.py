import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set a fixed random seed for reproducible seeding
random.seed(42)

from app import bcrypt, create_app, db
from app.models import Bookmark, Like, Match, Message, Notification, Profile, User

instance_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "instance"
)
if not os.path.exists(instance_dir):
    os.makedirs(instance_dir)
    print(f"Created instance folder: {instance_dir}")

app = create_app()


def seed():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        print("Seeding database...")

        users = []

        # ----------------------
        # 1. CREATE USERS
        # ----------------------
        for i in range(1, 11):
            user = User(
                email=f"user{i}@test.com",
                password_hash=bcrypt.generate_password_hash("password123").decode(
                    "utf-8"
                ),
                is_verified=True,
            )
            db.session.add(user)
            users.append(user)

        db.session.commit()

        # ----------------------
        # 2. CREATE PROFILES
        # ----------------------
        names = [
            "Alex",
            "Jordan",
            "Taylor",
            "Chris",
            "Sam",
            "Jamie",
            "Casey",
            "Drew",
            "Morgan",
            "Riley",
        ]

        for i, user in enumerate(users):
            profile = Profile(
                user_id=user.user_id,
                name=names[i],
                age=random.randint(18, 40),
                bio=f"Hi, I'm {names[i]}!",
                interests=random.sample(
                    ["music", "sports", "coding", "travel", "fitness", "gaming"], k=3
                ),
                gender=random.choice(["male", "female"]),
                gender_preference="all",
                relationship_goal="dating",
            )
            db.session.add(profile)

        db.session.commit()

        # ----------------------
        # 3. CREATE LIKES
        # ----------------------
        likes = []

        for user in users:
            others = [u for u in users if u.user_id != user.user_id]
            liked_users = random.sample(others, k=3)

            for target in liked_users:
                like = Like(
                    from_user_id=user.user_id, to_user_id=target.user_id, status="liked"
                )
                db.session.add(like)
                likes.append((user.user_id, target.user_id))

        db.session.commit()

        # ----------------------
        # 4. CREATE MATCHES (mutual likes)
        # ----------------------
        matches_created = set()

        for u1, u2 in likes:
            if (u2, u1) in likes and (u1, u2) not in matches_created:
                match = Match(user1_id=min(u1, u2), user2_id=max(u1, u2))
                db.session.add(match)
                matches_created.add((u1, u2))
                matches_created.add((u2, u1))

        db.session.commit()

        matches = Match.query.all()

        # ----------------------
        # 5. CREATE MESSAGES
        # ----------------------
        for match in matches:
            for _ in range(3):  # 3 messages per match
                sender = random.choice([match.user1_id, match.user2_id])
                receiver = (
                    match.user2_id if sender == match.user1_id else match.user1_id
                )

                message = Message(
                    sender_id=sender,
                    receiver_id=receiver,
                    content="Hey! How's it going?",
                )
                db.session.add(message)

        db.session.commit()

        # ----------------------
        # 6. CREATE NOTIFICATIONS
        # ----------------------
        for match in matches:
            notification = Notification(
                user_id=match.user1_id,
                type="match",
                message=f"You matched with user {match.user2_id}",
                from_user_id=match.user2_id,
            )
            db.session.add(notification)

        db.session.commit()

        # ----------------------
        # 7. CREATE BOOKMARKS
        # ----------------------
        for user in users:
            others = [u for u in users if u.user_id != user.user_id]
            bookmarked = random.choice(others)

            bookmark = Bookmark(
                user_id=user.user_id, bookmarked_user_id=bookmarked.user_id
            )
            db.session.add(bookmark)

        db.session.commit()

        # Log database information
        print("\n" + "=" * 50)
        print("DATABASE SEEDING COMPLETE - SUMMARY")
        print("=" * 50)

        users = User.query.all()
        print(f"\n📊 Users: {User.query.count()}")
        for user in users[:5]:  # Show first 5 users
            print(f"   - {user.email} (verified: {user.is_verified})")
        if len(users) > 5:
            print(f"   ... and {len(users) - 5} more")

        print(f"\n👤 Profiles: {Profile.query.count()}")
        print(f"❤️  Likes: {Like.query.count()}")
        print(f"🔥 Matches: {Match.query.count()}")
        print(f"💬 Messages: {Message.query.count()}")
        print(f"🔔 Notifications: {Notification.query.count()}")
        print(f"📌 Bookmarks: {Bookmark.query.count()}")

        # Show match details
        print("\n🔗 Matches (mutual likes):")
        for match in Match.query.all()[:5]:  # Show first 5 matches
            print(f"   - User {match.user1_id} ↔ User {match.user2_id}")
        if Match.query.count() > 5:
            print(f"   ... and {Match.query.count() - 5} more matches")

        print("\n" + "=" * 50)
        print("✅ Database seeded successfully!")
        print("=" * 50)


if __name__ == "__main__":
    seed()

import random
from app import create_app, db
from app.models import User, Profile, Like, Match, Message, Notification, Bookmark
from werkzeug.security import generate_password_hash


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
                password_hash=generate_password_hash("password123"),
                is_verified=True
            )
            db.session.add(user)
            users.append(user)

        db.session.commit()

        # ----------------------
        # 2. CREATE PROFILES
        # ----------------------
        names = ["Alex", "Jordan", "Taylor", "Chris", "Sam", "Jamie", "Casey", "Drew", "Morgan", "Riley"]

        for i, user in enumerate(users):
            profile = Profile(
                user_id=user.id,
                name=names[i],
                age=random.randint(18, 40),
                bio=f"Hi, I'm {names[i]}!",
                interests=random.sample(
                ["music", "sports", "coding", "travel", "fitness", "gaming"], k=3),
                gender=random.choice(["male", "female"]),
                gender_preference="all",
                relationship_goal="dating"
            )
            db.session.add(profile)

        db.session.commit()

        # ----------------------
        # 3. CREATE LIKES
        # ----------------------
        likes = []

        for user in users:
            others = [u for u in users if u.id != user.id]
            liked_users = random.sample(others, k=3)

            for target in liked_users:
                like = Like(
                    from_user_id=user.id,
                    to_user_id=target.id,
                    status="liked"
                )
                db.session.add(like)
                likes.append((user.id, target.id))

        db.session.commit()

        # ----------------------
        # 4. CREATE MATCHES (mutual likes)
        # ----------------------
        matches_created = set()

        for (u1, u2) in likes:
            if (u2, u1) in likes and (u1, u2) not in matches_created:
                match = Match(
                    user1_id=min(u1, u2),
                    user2_id=max(u1, u2)
                )
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
                receiver = match.user2_id if sender == match.user1_id else match.user1_id

                message = Message(
                    sender_id=sender,
                    receiver_id=receiver,
                    content="Hey! How's it going?"
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
                from_user_id=match.user2_id
            )
            db.session.add(notification)

        db.session.commit()

        # ----------------------
        # 7. CREATE BOOKMARKS
        # ----------------------
        for user in users:
            others = [u for u in users if u.id != user.id]
            bookmarked = random.choice(others)

            bookmark = Bookmark(
                user_id=user.id,
                bookmarked_user_id=bookmarked.id
            )
            db.session.add(bookmark)

        db.session.commit()

        print("✅ Database seeded successfully!")


if __name__ == "__main__":
    seed()
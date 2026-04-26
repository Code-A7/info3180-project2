# DriftDater - Dating Application

## a. Project Description

A full-stack dating application built with Vue 3 (frontend) and Flask (backend).

## b. Team Member Names and Roles

## c. Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+

### Steps

1. **Clone and enter directory:**
```bash
git clone <repository-url>
cd datingApp
```

2. **Set up Python virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

4. **Install Node.js dependencies:**
```bash
npm install
```

5. **Run the application:**

Both servers:
```bash
./start.sh
```

Or separately:

Backend (Terminal 1):
```bash
source .venv/bin/activate
python run.py
```

Frontend (Terminal 2):
```bash
npm run dev
```

## d. API Documentation

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| GET | `/api/auth/verify/<token>` | Verify email |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Get current user |

### Profile

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/profile` | Get my profile |
| POST | `/api/profile` | Create profile |
| PUT | `/api/profile` | Update profile |
| POST | `/api/profile/picture` | Upload profile picture |
| GET | `/api/profile/<id>` | View other profile |

### Matches

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/matches` | Get mutual matches |
| GET | `/api/matches/potential` | Get potential matches |
| POST | `/api/matches/like/<user_id>` | Like a user |
| POST | `/api/matches/dislike/<user_id>` | Dislike a user |
| POST | `/api/matches/pass/<user_id>` | Pass on a user |
| POST | `/api/matches/search` | Search profiles |
| GET | `/api/matches/bookmarks` | Get bookmarks |
| POST | `/api/matches/bookmark/<user_id>` | Bookmark user |
| DELETE | `/api/matches/bookmark/<user_id>` | Remove bookmark |

### Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications` | Get notifications |
| GET | `/api/notifications/unread-count` | Unread count |
| PUT | `/api/notifications/<id>/read` | Mark as read |
| PUT | `/api/notifications/read-all` | Mark all read |

### Messages

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/messages` | Get conversations |
| GET | `/api/messages/<user_id>` | Get messages |
| POST | `/api/messages/<user_id>` | Send message |
| PUT | `/api/messages/<message_id>/read` | Mark read |
| GET | `/api/messages/unread` | Unread count |
| POST | `/api/messages/typing/<user_id>` | Typing indicator |

## e. Deployed Application URL

## f. Known Issues and Limitations
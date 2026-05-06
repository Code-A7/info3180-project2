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

| Method | Endpoint                   | Description       |
| ------ | -------------------------- | ----------------- |
| POST   | `/api/auth/register`       | Register new user |
| GET    | `/api/auth/verify/<token>` | Verify email      |
| POST   | `/api/auth/login`          | Login             |
| POST   | `/api/auth/logout`         | Logout            |
| GET    | `/api/auth/me`             | Get current user  |

### Profile

| Method | Endpoint               | Description            |
| ------ | ---------------------- | ---------------------- |
| GET    | `/api/profile`         | Get my profile         |
| POST   | `/api/profile`         | Create profile         |
| PUT    | `/api/profile`         | Update profile         |
| POST   | `/api/profile/picture` | Upload profile picture |
| GET    | `/api/profile/<id>`    | View other profile     |

### Matches

| Method | Endpoint                          | Description           |
| ------ | --------------------------------- | --------------------- |
| GET    | `/api/matches`                    | Get mutual matches    |
| GET    | `/api/matches/potential`          | Get potential matches |
| POST   | `/api/matches/like/<user_id>`     | Like a user           |
| POST   | `/api/matches/dislike/<user_id>`  | Dislike a user        |
| POST   | `/api/matches/pass/<user_id>`     | Pass on a user        |
| POST   | `/api/matches/search`             | Search profiles       |
| GET    | `/api/matches/bookmarks`          | Get bookmarks         |
| POST   | `/api/matches/bookmark/<user_id>` | Bookmark user         |
| DELETE | `/api/matches/bookmark/<user_id>` | Remove bookmark       |

### Notifications

| Method | Endpoint                          | Description       |
| ------ | --------------------------------- | ----------------- |
| GET    | `/api/notifications`              | Get notifications |
| GET    | `/api/notifications/unread-count` | Unread count      |
| PUT    | `/api/notifications/<id>/read`    | Mark as read      |
| PUT    | `/api/notifications/read-all`     | Mark all read     |

### Messages

| Method | Endpoint                          | Description       |
| ------ | --------------------------------- | ----------------- |
| GET    | `/api/messages`                   | Get conversations |
| GET    | `/api/messages/<user_id>`         | Get messages      |
| POST   | `/api/messages/<user_id>`         | Send message      |
| PUT    | `/api/messages/<message_id>/read` | Mark read         |
| GET    | `/api/messages/unread`            | Unread count      |
| POST   | `/api/messages/typing/<user_id>`  | Typing indicator  |

## USER AUTHENTICATION

The application implements a secure authentication system that ensures safe access and account management.

### Features

- **User Registration & Email Verification**
  - Users register with a unique email address
  - Email verification is required via token-based system
  - Users can request verification email resend

- **Secure Authentication**
  - Login and logout functionality
  - Session/token-based authentication
  - Passwords are hashed using bcrypt

- **Account Recovery**
  - Forgot password functionality
  - Password reset using secure tokens

- **Session Management**
  - Retrieve currently authenticated user
  - Token refresh support

### API Endpoints

| Method | Endpoint | Description |
|--------|---------|------------|
| POST | `/api/auth/register` | Register user |
| GET | `/api/auth/verify/<token>` | Verify email |
| POST | `/api/auth/resend-verification` | Resend verification email |
| POST | `/api/auth/login` | Login user |
| POST | `/api/auth/logout` | Logout user |
| POST | `/api/auth/forgot-password` | Request password reset |
| POST | `/api/auth/reset-password` | Reset password |
| POST | `/api/auth/refresh` | Refresh authentication token |
| GET | `/api/auth/me` | Get current authenticated user |

---

## PROFILE MANAGEMENT

The application provides full profile management functionality, allowing users to create and manage detailed personal profiles.

### Features

- **Profile Creation & Editing**
  - Users can create, retrieve, and update their profiles

- **Profile Information**
  - Name, age, and bio/description
  - Location and geographic preferences
  - Interests (minimum requirement supported)
  - Additional custom fields

- **Profile Media**
  - Profile picture upload capability

- **Profile Access**
  - Users can view other user profiles

### API Endpoints

| Method | Endpoint | Description |
|--------|---------|------------|
| POST | `/api/profile` | Create profile |
| GET | `/api/profile` | Get own profile |
| PUT | `/api/profile` | Update profile |
| POST | `/api/profile/picture` | Upload profile picture |
| GET | `/api/profile/<int:user_id>` | View another user profile |

---

## SEARCH & DISCOVERY

The application provides a dynamic search and discovery system for finding and interacting with potential matches.

### Features

- **Search Functionality**
  - Users can search for profiles using:
    - Age range
    - Interests
    - Additional filtering criteria

- **Match Discovery**
  - View potential matches generated by the matching algorithm
  - Matching considers:
    - Shared interests
    - Compatibility scoring
    - Additional backend-defined criteria

- **User Interaction**
  - Like, dislike, or pass on other users
  - Match scoring system available

- **Bookmarks / Favorites**
  - Users can bookmark profiles
  - Retrieve and manage saved profiles

- **Filtering & Browsing**
  - Browse potential matches
  - Apply filters via search endpoint

### API Endpoints

| Method | Endpoint | Description |
|--------|---------|------------|
| GET | `/api/matches/potential` | View potential matches |
| POST | `/api/matches/search` | Search profiles |
| POST | `/api/matches/like/<int:to_user_id>` | Like a user |
| POST | `/api/matches/dislike/<int:to_user_id>` | Dislike a user |
| POST | `/api/matches/pass/<int:to_user_id>` | Pass on a user |
| GET | `/api/matches/score/<int:to_user_id>` | View match score |
| GET | `/api/matches/bookmarks` | Get bookmarked profiles |
| POST | `/api/matches/bookmark/<int:to_user_id>` | Add bookmark |
| DELETE | `/api/matches/bookmark/<int:to_user_id>` | Remove bookmark |

## e. Deployed Application URL

## f. Known Issues and Limitations

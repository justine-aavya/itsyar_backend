## `README.md`

```markdown
# 🚀 ItsYar Backend API

> Learning & Hackathon Platform — powered by FastAPI + Palantir Foundry

A production-grade backend serving courses, hackathons, quizzes, and leaderboards. Auth lives in PostgreSQL; all training data lives in Palantir Foundry via the OSDK.

---

## 📐 Architecture

```
┌──────────────────┐         ┌────────────────────┐         ┌──────────────────────┐
│                  │  HTTP    │                    │  OSDK   │                      │
│   React Frontend │ ──────► │   FastAPI Backend   │ ──────► │   Palantir Foundry   │
│   (Port 3000)   │         │   (Port 8000)      │         │   (Ontology + Media) │
│                  │         │                    │         │                      │
└──────────────────┘         └────────┬───────────┘         └──────────────────────┘
                                      │
                                      │ SQLAlchemy
                                      ▼
                             ┌─────────────────┐
                             │   PostgreSQL     │
                             │   (Auth Only)    │
                             └─────────────────┘
```

| Concern | Storage |
|---------|---------|
| Users, passwords, JWT tokens | PostgreSQL |
| Courses, events, quizzes, enrollments, leaderboard | Palantir Foundry (OSDK) |
| Videos | Foundry Blobster / Local static |
| PDFs | Foundry Media Sets |

---

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | FastAPI | 0.115+ |
| Language | Python | 3.10+ |
| Auth | JWT (python-jose) + bcrypt | — |
| ORM | SQLAlchemy | 2.0+ |
| Database | PostgreSQL | 14+ |
| Data Platform | Palantir Foundry OSDK | — |
| SDK Package | `training_and_hackathon_sdk` | 0.12.0 |
| HTTP Client | Requests | 2.32+ |

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/itsyar_backend.git
cd itsyar_backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Activate:
# Windows (PowerShell)
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Palantir Foundry SDK

```powershell
# Windows PowerShell
$env:FOUNDRY_TOKEN="your-foundry-token"

pip install training_and_hackathon_sdk==0.12.0 --upgrade `
  --index-url "https://user:$env:FOUNDRY_TOKEN@aavya.palantirfoundry.com/artifacts/api/repositories/ri.artifacts.main.repository.ade321f2-0f3d-4957-b97c-1da091e5bd2e/contents/release/pypi/simple" `
  --extra-index-url "https://user:$env:FOUNDRY_TOKEN@aavya.palantirfoundry.com/artifacts/api/repositories/ri.foundry-sdk-asset-bundle.main.artifacts.repository/contents/release/pypi/simple"
```

```bash
# macOS / Linux
export FOUNDRY_TOKEN="your-foundry-token"

pip install training_and_hackathon_sdk==0.12.0 --upgrade \
  --index-url "https://user:${FOUNDRY_TOKEN}@aavya.palantirfoundry.com/artifacts/api/repositories/ri.artifacts.main.repository.ade321f2-0f3d-4957-b97c-1da091e5bd2e/contents/release/pypi/simple" \
  --extra-index-url "https://user:${FOUNDRY_TOKEN}@aavya.palantirfoundry.com/artifacts/api/repositories/ri.foundry-sdk-asset-bundle.main.artifacts.repository/contents/release/pypi/simple"
```

### 5. Setup PostgreSQL

Create the database:
```sql
CREATE DATABASE itsyar;
```

> Tables are auto-created on first run via SQLAlchemy `metadata.create_all()`.

### 6. Configure Environment Variables

Create a `.env` file in the project root:

```env
# ─── Database ───────────────────────────────────
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/itsyar

# ─── Auth / JWT ─────────────────────────────────
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ─── Palantir Foundry ───────────────────────────
FOUNDRY_URL=https://aavya.palantirfoundry.com
FOUNDRY_CLIENT_ID=your-client-id
FOUNDRY_CLIENT_SECRET=your-client-secret
FOUNDRY_ONTOLOGY_RID=your-ontology-rid
```

### 7. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ API running at: `http://localhost:8000`
📚 Swagger docs: `http://localhost:8000/docs`

---

## 📁 Project Structure

```
itsyar_backend/
│
├── app/
│   ├── main.py                          # App entry, middleware, startup
│   │
│   ├── api/
│   │   ├── deps.py                      # get_current_user dependency
│   │   └── router.py                    # Root API router (mounts sub-routers)
│   │
│   ├── core/
│   │   ├── config.py                    # Settings (from .env)
│   │   └── security.py                  # JWT creation, password hashing
│   │
│   ├── db/
│   │   └── session.py                   # SQLAlchemy engine + session
│   │
│   ├── models/
│   │   ├── user.py                      # User SQLAlchemy model
│   │   │
│   │   ├── auth/
│   │   │   ├── router.py               # /api/auth/* endpoints
│   │   │   └── schemas.py              # Auth request/response schemas
│   │   │
│   │   └── courses/
│   │       ├── router.py               # /api/courses/* endpoints
│   │       └── schemas.py              # Course request/response schemas
│   │
│   └── integrations/
│       └── palantir/
│           ├── foundry_client.py        # OSDK client singleton
│           └── foundry_service.py       # All Foundry data operations
│
├── static/
│   └── videos/                          # Local video files (course_1.mp4, etc.)
│
├── .env                                 # Environment variables (DO NOT COMMIT)
├── .gitignore                           # Git ignore rules
├── requirements.txt                     # Python dependencies
└── README.md                            # This file
```

---

## 🔌 API Reference

### Response Format

All responses follow a consistent format:

**Success:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error:**
```json
{
  "error": {
    "data": {
      "message": "Human-readable error description"
    }
  }
}
```

> ⚠️ All response keys are **camelCase** (auto-converted via middleware).

---

### 🔐 Auth — `/api/auth`

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/signup` | ❌ | Create new account |
| POST | `/login` | ❌ | Authenticate user |
| POST | `/refresh-token` | ❌ | Refresh expired access token |
| POST | `/forgot-password` | ❌ | Request password reset link |
| POST | `/reset-password` | ❌ | Set new password with reset token |
| GET | `/me` | ✅ | Get current user profile |

#### `POST /api/auth/signup`

**Request:**
```json
{
  "fullName": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "confirmPassword": "SecurePass123",
  "userType": "Student",
  "interest": "AI & Machine Learning",
  "acceptTerms": true
}
```

**Response (201):**
```json
{
  "success": true,
  "accessToken": "eyJ...",
  "refreshToken": "eyJ...",
  "tokenType": "bearer",
  "user": {
    "id": "uuid",
    "email": "john@example.com",
    "fullName": "john doe",
    "role": "Student",
    "learningInterest": "AI & Machine Learning"
  }
}
```

#### `POST /api/auth/login`

**Request:**
```json
{
  "email": "john@example.com",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "success": true,
  "accessToken": "eyJ...",
  "refreshToken": "eyJ...",
  "tokenType": "bearer",
  "user": {
    "id": "uuid",
    "email": "john@example.com",
    "fullName": "john doe",
    "role": "Student",
    "learningInterest": "AI & Machine Learning"
  }
}
```

---

### 📚 Courses — `/api/courses`

| Method | Endpoint | Auth | Enrolled | Description |
|--------|----------|------|----------|-------------|
| GET | `/look` | ✅ | ❌ | Browse/search catalog |
| GET | `/my` | ✅ | — | My enrolled courses |
| GET | `/{id}` | ✅ | ❌ | Course detail page |
| POST | `/{id}/enroll` | ✅ | ❌→✅ | Enroll in course |
| GET | `/{id}/modules` | ✅ | ✅ | Full curriculum |
| GET | `/{id}/modules/{mid}/content` | ✅ | ✅ | Lesson video + PDF |
| GET | `/{id}/modules/{mid}/quiz` | ✅ | ✅ | Quiz questions |
| POST | `/{id}/modules/{mid}/quiz/submit` | ✅ | ✅ | Submit & auto-grade |
| GET | `/{id}/pdf` | ✅ | ✅ | Stream PDF from Foundry |
| GET | `/{id}/progress` | ✅ | ❌ | Check completion status |

#### `GET /api/courses/look`

**Params:** `q` (search), `offset`, `limit`, `category`, `level` — all optional

**Response:**
```json
{
  "success": true,
  "courses": [
    {
      "id": "1",
      "title": "Welcome to the World of Palatir",
      "tag": "Palantir",
      "duration": "20 Minutes",
      "instructor": "Harshpreet Kaur Arora",
      "description": "An introductory course...",
      "image": null,
      "badge": null,
      "level": "Beginner"
    }
  ],
  "total": 1,
  "offset": 0,
  "limit": 6,
  "query": null
}
```

#### `GET /api/courses/{id}/modules`

**Response:**
```json
{
  "success": true,
  "course": {
    "id": "1",
    "title": "Welcome to the World of Palatir",
    "description": "...",
    "curriculum": [
      {
        "id": 1,
        "title": "Welcome to the World of Palatir",
        "lessons": [
          {
            "id": "1-1",
            "title": "Welcome to the World of Palatir",
            "videoUrl": "https://aavya.palantirfoundry.com/workspace/preview-app/ri.blobster...",
            "summary": "This course covers...",
            "materials": [
              { "id": "m-1-pdf", "title": "Course PDF Notes", "type": "pdf", "meta": "PDF Document" }
            ]
          }
        ]
      }
    ]
  }
}
```

#### `GET /api/courses/{id}/modules/{mid}/quiz`

**Response:**
```json
{
  "success": true,
  "quiz": {
    "id": "quiz_1_1",
    "title": "Module Test: Welcome to the World of Palatir",
    "path": "Welcome to the World of Palatir",
    "timeLimit": 10,
    "questions": [
      {
        "id": "q_001",
        "text": "What is the primary purpose of Palantir Foundry?",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correctAnswer": "a"
      }
    ]
  }
}
```

#### `POST /api/courses/{id}/modules/{mid}/quiz/submit`

**Request:**
```json
{
  "answers": [
    { "questionId": "q_001", "answer": ["a"] },
    { "questionId": "q_002", "answer": ["b"] }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "score": 80,
  "passed": true,
  "total": 5,
  "correct": 4,
  "message": "You scored 4/5 (80%) — Course completed! 🎉"
}
```

---

## 🔒 Authentication

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

Token lifecycle:
1. Login/Signup → receive `accessToken` + `refreshToken`
2. Use `accessToken` for API calls (expires in 30 min)
3. When expired → call `/refresh-token` with `refreshToken`
4. If refresh token is invalid → user must login again

---

## 🏗️ Middleware

| Middleware | Purpose |
|-----------|---------|
| **CORS** | Allows all origins (development mode) |
| **CamelCase** | Auto-converts all JSON response keys from `snake_case` → `camelCase` |
| **Validation Handler** | Wraps Pydantic errors in standard `error.data.message` format |

---

## 🗄️ Foundry Object Types Used

| Object Type | Purpose |
|-------------|---------|
| `Courses` | Course catalog |
| `VanyarEnrolment` | User ↔ Course enrollment records |
| `Quizes` | Quiz questions + answer keys |
| `VanyarEvent` | Events / Hackathons |
| `VanyarChallenge` | Challenges within events |
| `Hackathons` | Hackathon listings |
| `VanyarUser` | User mirror in Foundry |
| `VanyarTrack` | Learning tracks |
| `VanyarLeaderboardEntry` | Leaderboard scores |
| `ReviewsFeedback` | Platform reviews |

---

## 🚀 Deployment

### Production checklist:
- [ ] Set strong `SECRET_KEY` in `.env`
- [ ] Set `CORS` to specific frontend domain (not `*`)
- [ ] Use environment-specific Foundry credentials
- [ ] Enable HTTPS
- [ ] Set `ACCESS_TOKEN_EXPIRE_MINUTES` appropriately
- [ ] Run with gunicorn: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker`

---

## 👥 Team

- **Backend:** ItsYar Engineering
- **Data Platform:** Palantir Foundry
- **Frontend:** React

---

## 📄 License

Private — ItsYar Team. All rights reserved.
```

---

Save this as `README.md` in your project root. Want me to update anything in it?

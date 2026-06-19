Here's your `README.md`:

```markdown
# ItsYar Backend

Enterprise learning platform backend built with FastAPI, PostgreSQL, and Palantir Foundry OSDK.

## Tech Stack

- **Framework:** FastAPI (Python 3.12)
- **Database:** PostgreSQL (authentication)
- **Data Platform:** Palantir Foundry OSDK (courses, events, quizzes)
- **Auth:** JWT (access + refresh tokens)

## Quick Start

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/itsyar_backend.git
cd itsyar_backend

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Foundry SDK (requires token)
$env:FOUNDRY_TOKEN="your_token_here"
pip install training_and_hackathon_sdk==0.10.0 --no-deps `
  --index-url "https://user:$env:FOUNDRY_TOKEN@aavya.palantirfoundry.com/artifacts/api/repositories/ri.artifacts.main.repository.ade321f2-0f3d-4957-b97c-1da091e5bd2e/contents/release/pypi/simple"

# 5. Setup .env file (see Environment Variables below)

# 6. Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Environment Variables

Create a `.env` file in the root:

```env
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/itsyar

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Palantir Foundry
FOUNDRY_URL=https://aavya.palantirfoundry.com
FOUNDRY_CLIENT_ID=your_client_id
FOUNDRY_CLIENT_SECRET=your_client_secret
FOUNDRY_ONTOLOGY_RID=your_ontology_rid
```

## API Documentation

Swagger UI: `http://localhost:8000/docs`

## Architecture

```
PostgreSQL (Auth)          Palantir Foundry (Data)
├── Signup                 ├── Courses
├── Login                  ├── VanyarEnrolment
├── Password Reset         ├── Quizes
├── Token Refresh          ├── VanyarEvent
└── Session Management     ├── VanyarTrack
                           └── Hackathons (future)
```

## API Endpoints

### Auth (`/api/auth`)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/signup` | Register new user (+ sync to Foundry) |
| POST | `/login` | Login, returns JWT tokens |
| POST | `/refresh-token` | Refresh expired access token |
| POST | `/forgot-password` | Request password reset |
| POST | `/reset-password` | Reset password with token |
| GET | `/me` | Get current user profile |

### Courses (`/api/courses`)

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/` | List all courses | JWT |
| GET | `/search?q=` | Search courses | JWT |
| GET | `/my` | My enrolled courses | JWT |
| GET | `/{course_id}` | Course detail | JWT |
| POST | `/{course_id}/enroll` | Enroll in course | JWT |
| GET | `/{course_id}/modules` | List modules | JWT + Enrolled |
| GET | `/{course_id}/modules/{module_id}/content` | Video + PDF | JWT + Enrolled |
| GET | `/{course_id}/modules/{module_id}/quiz` | Quiz questions | JWT + Enrolled |
| POST | `/{course_id}/modules/{module_id}/quiz/submit` | Submit quiz | JWT + Enrolled |
| GET | `/{course_id}/progress` | Completion status | JWT |

### Events (`/api/foundry`)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/status` | Foundry connection check |
| GET | `/events` | List all events |
| GET | `/events/{id}` | Event detail |
| POST | `/events/{id}/enrol` | Register for event |
| GET | `/tracks` | List learning tracks |
| GET | `/stats` | Platform statistics |

## Response Format

**Success:**
```json
{"success": true, "data": {...}}
```

**Error:**
```json
{"error": {"data": {"message": "Error description"}}}
```

## Authorization

All endpoints (except login/signup) require:
```
Authorization: Bearer <access_token>
```

Token obtained from login/signup response: `accessToken` field.

## Foundry OSDK Integration

### Objects Used
- `Courses` — Course catalog
- `VanyarEnrolment` — Enrollment tracking
- `Quizes` — Quiz questions + answer key
- `VanyarEvent` — Events/hackathons
- `VanyarUser` — User profiles (synced on signup)
- `VanyarTrack` — Learning tracks

### Actions Used
- `create_vanyar_user` — Sync user to Foundry on signup
- `create_enrolment` — Enroll user in course
- `mark_complete` — Mark course as completed (after quiz pass)
- `register_for_event` — Register for events

## Quiz Grading

- Answer format: Array (e.g., `["B"]` or `["B", "D"]`)
- Passing threshold: 70%
- On pass: automatically calls `mark_complete` action
- Comparison: case-insensitive set matching

## CamelCase Middleware

All JSON responses automatically convert `snake_case` → `camelCase` for frontend compatibility. Python code stays snake_case internally.

## Network Access

```bash
# Allow external access (Windows Firewall)
New-NetFirewallRule -DisplayName "Allow Port 8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

Server accessible at: `http://<your-ip>:8000`

## Updating Foundry SDK

```powershell
$env:FOUNDRY_TOKEN="your_token"
pip uninstall training_and_hackathon_sdk -y
pip install training_and_hackathon_sdk==X.X.X --no-deps `
  --index-url "https://user:$env:FOUNDRY_TOKEN@aavya.palantirfoundry.com/artifacts/api/repositories/ri.artifacts.main.repository.ade321f2-0f3d-4957-b97c-1da091e5bd2e/contents/release/pypi/simple"
```

## Project Structure

```
app/
├── main.py                          # FastAPI app + middleware
├── api/
│   ├── router.py                    # Route registration
│   └── deps.py                      # Auth dependencies
├── core/
│   ├── config.py                    # Settings
│   └── security.py                  # JWT + password hashing
├── db/
│   ├── session.py                   # Database connection
│   └── base.py                      # SQLAlchemy base
├── models/
│   ├── user.py                      # User SQLAlchemy model
│   ├── auth/
│   │   ├── router.py                # Auth endpoints
│   │   └── schemas.py               # Auth Pydantic models
│   └── courses/
│       ├── router.py                # Course endpoints
│       └── schemas.py               # Course Pydantic models
└── integrations/
    └── palantir/
        ├── foundry_client.py        # OSDK connection manager
        └── foundry_service.py       # All Foundry data operations
```
```

Save as `README.md` in your project root, then:

```powershell
git add README.md
git commit -m "docs: add README"
git push origin main
```

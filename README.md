## `README.md`

```markdown
# ItsYar Backend

Backend API for the ItsYar Learning & Hackathon Platform — built with FastAPI, PostgreSQL, and Palantir Foundry OSDK.

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   React UI  │ ──► │  FastAPI Backend  │ ──► │ Palantir Foundry │
│  (Frontend) │     │   (This Repo)    │     │     (OSDK)       │
└─────────────┘     └──────────────────┘     └─────────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  PostgreSQL  │
                    │  (Auth Only) │
                    └──────────────┘
```

- **Auth (JWT)** → PostgreSQL
- **Data (Courses, Events, Hackathons)** → Palantir Foundry OSDK

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | FastAPI (Python) |
| Auth | JWT (python-jose) + bcrypt |
| Database | PostgreSQL (SQLAlchemy ORM) |
| Data Platform | Palantir Foundry (OSDK) |
| SDK | `training_and_hackathon_sdk` |

## API Endpoints

### Auth (`/api/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signup` | Create account + auto-login |
| POST | `/login` | Authenticate user |
| POST | `/refresh-token` | Refresh access token |
| POST | `/forgot-password` | Request password reset |
| POST | `/reset-password` | Reset password with token |
| GET | `/me` | Get current user profile |

### Courses (`/api/courses`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/look` | Browse/search course catalog |
| GET | `/my` | User's enrolled courses |
| GET | `/{id}` | Course detail |
| POST | `/{id}/enroll` | Enroll in course |
| GET | `/{id}/modules` | Full curriculum (modules → lessons) |
| GET | `/{id}/modules/{mid}/content` | Lesson content (video + PDF) |
| GET | `/{id}/modules/{mid}/quiz` | Quiz questions |
| POST | `/{id}/modules/{mid}/quiz/submit` | Submit quiz + auto-grade |
| GET | `/{id}/pdf` | Stream PDF from Foundry |
| GET | `/{id}/progress` | Enrollment progress |

### Events & Hackathons (`/api/events`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List all events |
| GET | `/{id}` | Event detail |
| POST | `/{id}/register` | Register for event |

## Setup

### Prerequisites
- Python 3.10+
- PostgreSQL
- Palantir Foundry access (Client ID + Secret)

### Installation

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/itsyar_backend.git
cd itsyar_backend

# Virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Install Foundry SDK
$env:FOUNDRY_TOKEN="your-token-here"
pip install training_and_hackathon_sdk==0.12.0 --upgrade `
  --index-url "https://user:$env:FOUNDRY_TOKEN@aavya.palantirfoundry.com/artifacts/api/repositories/ri.artifacts.main.repository.ade321f2-0f3d-4957-b97c-1da091e5bd2e/contents/release/pypi/simple" `
  --extra-index-url "https://user:$env:FOUNDRY_TOKEN@aavya.palantirfoundry.com/artifacts/api/repositories/ri.foundry-sdk-asset-bundle.main.artifacts.repository/contents/release/pypi/simple"
```

### Environment Variables

Create a `.env` file:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/itsyar

# Auth
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Palantir Foundry
FOUNDRY_URL=https://aavya.palantirfoundry.com
FOUNDRY_CLIENT_ID=your-client-id
FOUNDRY_CLIENT_SECRET=your-client-secret
FOUNDRY_ONTOLOGY_RID=your-ontology-rid
```

### Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: `http://localhost:8000/docs`

## Project Structure

```
itsyar_backend/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── api/
│   │   ├── deps.py             # Auth dependencies
│   │   └── router.py           # Main API router
│   ├── core/
│   │   ├── config.py           # Settings
│   │   └── security.py         # JWT + hashing
│   ├── db/
│   │   └── session.py          # PostgreSQL connection
│   ├── models/
│   │   ├── user.py             # User SQLAlchemy model
│   │   ├── auth/
│   │   │   ├── router.py       # Auth endpoints
│   │   │   └── schemas.py      # Auth Pydantic schemas
│   │   └── courses/
│   │       ├── router.py       # Course endpoints
│   │       └── schemas.py      # Course Pydantic schemas
│   └── integrations/
│       └── palantir/
│           ├── foundry_client.py   # OSDK client manager
│           └── foundry_service.py  # Foundry data layer
├── static/
│   └── videos/                 # Local video files
├── .env                        # Environment variables (DO NOT COMMIT)
├── .gitignore
├── requirements.txt
└── README.md
```

## Response Format

**Success:**
```json
{ "success": true, "data": { ... } }
```

**Error:**
```json
{ "error": { "data": { "message": "Human-readable error" } } }
```

All responses use **camelCase** keys (auto-converted from snake_case via middleware).

## License

Private — ItsYar Team
```

---

## `requirements.txt`

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.31
psycopg2-binary==2.9.9
pydantic[email]==2.8.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.1.3
python-dotenv==1.0.1
requests==2.32.3
python-multipart==0.0.9
```

> **Note:** `training_and_hackathon_sdk` is installed separately from the Foundry private registry (see Setup instructions above).

---

Save these as `README.md` and `requirements.txt` in your project root (`C:\Users\justi\OneDrive\Desktop\itsyar_backend\`).


from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import engine
from app.db.base import Base

import os
from app.integrations.palantir.foundry_client import verify_foundry_credentials

from app.api.router import api_router
from app.api.deps import get_current_user
from app.models.user import User
from app.models.auth.schemas import UserResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="itsyar Architecture Engine", version="3.0.0", docs_url="/docs")

@app.on_event("startup")
def diagnostic_check():
    print("\n[DIAGNOSTIC] Testing Palantir Foundry Client Credentials...")
    
    # Pull variables directly out of your current .env setup
    url = os.getenv("FOUNDRY_URL", "https://your-company.palantirfoundry.com")
    client_id = os.getenv("FOUNDRY_CLIENT_ID")
    client_secret = os.getenv("FOUNDRY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("[DIAGNOSTIC WARNING] Missing credentials in .env file. Skipping check.")
        return

    result = verify_foundry_credentials(url, client_id, client_secret)
    
    if result["connected"]:
        print(f"✅ {result['message']}\n")
    else:
        print(f"❌ CONNECTION FAILED: {result['message']}")
        print(f"Details: {result.get('error_details', 'N/A')}\n")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core Global Prefix Mount Point
app.include_router(api_router, prefix="/api")

@app.get("/api/auth/me", response_model=UserResponse, tags=["Authentication Layer"])
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@app.get("/", tags=["System Diagnostics"])
def system_health_status():
    return {"status": "healthy, iysyar is running."}
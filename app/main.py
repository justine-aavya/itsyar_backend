# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from app.database import engine, Base
# from app.routers import auth, events

# # Create all tables on startup
# Base.metadata.create_all(bind=engine)

# app = FastAPI(
#     title="ITSYAR Backend",
#     description="Backend API for the ITSYAR learning & hackathon platform",
#     version="0.2.0",
# )

# # CORS — allow React frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",
#         "http://localhost:5173",
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Register routers
# app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(events.router, prefix="/api", tags=["Events & Data"])


# @app.get("/", tags=["Health"])
# def root():
#     return {"status": "ok", "message": "ITSYAR Backend is running 🚀", "version": "0.2.0"}

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import engine
from app.db.base import Base

from app.api.router import api_router
from app.api.deps import get_current_user
from app.models.user import User
from app.models.auth.schemas import UserResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="itsyar Architecture Engine", version="3.0.0", docs_url="/docs")

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
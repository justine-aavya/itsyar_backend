
from fastapi import APIRouter
from app.models.auth.router import router as auth_router
from app.models.landing.router import router as landing_router
from app.models.hackathons.router import router as hackathons_router
from app.models.courses.router import router as courses_router


api_router = APIRouter()

# Structural Mounting Hierarchy

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication Layer"])
api_router.include_router(landing_router, prefix="/landing", tags=["Public Landing Configurations"])
api_router.include_router(hackathons_router, prefix="/foundry", tags=["Palantir Foundry Core Pipeline"])
api_router.include_router(courses_router, prefix="/courses", tags=["Course Management"])
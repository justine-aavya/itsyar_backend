# app/routers/events.py
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.core.security import get_current_user, require_role
from app.models.user import User
from app.integrations.palantir.foundry_client import verify_foundry_credentials
from app.integrations.palantir import foundry_service

router = APIRouter()


class EventRegistration(BaseModel):
    event_id: str


# ─────────────────────────────────────────────
# Status (Public)
# ─────────────────────────────────────────────

@router.get("/status")
def foundry_status():
    """Performs a live cryptographic handshake verification check with Palantir."""
    url = os.getenv("FOUNDRY_URL", "")
    client_id = os.getenv("FOUNDRY_CLIENT_ID") or os.getenv("CLIENT_ID", "")
    client_secret = (
        os.getenv("FOUNDRY_CLIENT_SECRET")
        or os.getenv("CLIENT_SECRET")
        or os.getenv("foundry_client_secret", "")
    )

    if not all([url, client_id, client_secret]):
        return {
            "foundry_configured": False,
            "mode": "mock",
            "message": "Running with mock data (Foundry env vars missing)"
        }

    check = verify_foundry_credentials(url, client_id, client_secret)
    if check["connected"]:
        return {
            "foundry_configured": True,
            "mode": "live",
            "message": "Connected to Foundry! Credentials verified successfully."
        }
    else:
        return {
            "foundry_configured": False,
            "mode": "error",
            "message": f"Configuration error: {check['message']}"
        }


# ─────────────────────────────────────────────
# READ: Stats (Admin & Mentor only)
# ─────────────────────────────────────────────

@router.get("/stats")
def platform_stats(current_user: User = Depends(require_role(["Admin", "Mentor"]))):
    """Get platform-wide statistics."""
    try:
        return foundry_service.get_platform_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# READ: Events (All authenticated users)
# ─────────────────────────────────────────────

@router.get("/events")
def list_events(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user)
):
    """List all events from Palantir OSDK with optional status filtering(ACTIVE)."""
    try:
        events = foundry_service.get_all_events(status_filter=status_filter)
        return {"ok": True, "events": events, "count": len(events)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OSDK data retrieval failed: {str(e)}"
        )


@router.get("/events/{event_id}")
def get_event(event_id: str, current_user: User = Depends(get_current_user)):
    """Get a single event by ID."""
    try:
        event = foundry_service.get_event_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        return {"ok": True, "data": event}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/events/{event_id}/challenges")
def event_challenges(event_id: str, current_user: User = Depends(get_current_user)):
    """Get challenges for a specific event."""
    try:
        challenges = foundry_service.get_challenges(event_id)
        return {"event_id": event_id, "challenges": challenges, "count": len(challenges)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# READ: Tracks (All authenticated users)
# ─────────────────────────────────────────────

@router.get("/tracks")
def list_tracks(current_user: User = Depends(get_current_user)):
    """List all learning tracks."""
    try:
        tracks = foundry_service.get_all_tracks()
        return {"tracks": tracks, "count": len(tracks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# READ: Hackathons (All authenticated users)
# ─────────────────────────────────────────────

@router.get("/hackathons")
def list_hackathons(current_user: User = Depends(get_current_user)):
    """List all hackathons from Palantir."""
    try:
        hackathons = foundry_service.get_all_hackathons()
        return {"ok": True, "hackathons": hackathons, "count": len(hackathons)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# READ: Courses (All authenticated users)
# ─────────────────────────────────────────────

@router.get("/courses")
def list_courses(current_user: User = Depends(get_current_user)):
    """List all courses."""
    try:
        courses = foundry_service.get_all_courses()
        return {"ok": True, "courses": courses, "count": len(courses)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# READ: Leaderboard
# ─────────────────────────────────────────────

@router.get("/leaderboard")
def get_leaderboard(
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """Get top leaderboard entries from Palantir."""
    try:
        entries = foundry_service.get_top_leaderboard(limit=limit)
        return {"ok": True, "leaderboard": entries, "count": len(entries)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────
# WRITE: Register/Enrol for Event
# ─────────────────────────────────────────────

@router.post("/events/{event_id}/enrol")
def enroll_in_event(
    event_id: str,
    current_user: User = Depends(require_role(["Student", "Participant"])),
):
    """Register for an event. Checks for duplicates first."""
    try:
        # Check if already enrolled
        already_enrolled = foundry_service.check_event_enrollment(
            event_id=event_id,
            user_id=str(current_user.id)
        )
        if already_enrolled:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You are already enrolled in this event"
            )

        # Proceed with registration
        result = foundry_service.register_for_event(
            event_id=event_id,
            user_id=str(current_user.id)
        )

        if isinstance(result, dict) and result.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message")
            )

        return {"ok": True, "data": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Foundry Action Rejected: {str(e)}"
        )


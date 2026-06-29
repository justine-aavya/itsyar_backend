from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from app.api.deps import get_current_user
from app.models.user import User
from app.integrations.palantir import foundry_service
from .schemas import HackathonRegistrationRequest

router = APIRouter()


def error_response(status_code: int, message: str):
    return JSONResponse(
        status_code=status_code,
        content={"error": {"data": {"message": message}}}
    )


# ═══════════════════════════════════════════════════════════════
# LIST ALL HACKATHONS
# ═══════════════════════════════════════════════════════════════

@router.get("", status_code=status.HTTP_200_OK)
def list_hackathons(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """List all hackathons. Optional filter by status (e.g., ?status_filter=Open)."""
    try:
        result = foundry_service.get_all_hackathons(status_filter=status_filter)
        return {"success": True, "count": len(result), "hackathons": result}

    except HTTPException:
        raise
    except Exception as e:
        return error_response(500, f"Failed to fetch hackathons: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# USER'S CURRENT TEAM (must be BEFORE /{hackathon_id})
# ═══════════════════════════════════════════════════════════════

@router.get("/user/current-team", status_code=status.HTTP_200_OK)
def get_user_team(
    current_user: User = Depends(get_current_user),
):
    """Get the current user's team info."""
    try:
        team = foundry_service.get_user_team(user_id=str(current_user.id))

        if not team:
            return {"success": True, "team": None, "message": "No team found"}

        return {"success": True, "team": team}

    except HTTPException:
        raise
    except Exception as e:
        return error_response(500, f"Failed to fetch team: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# HACKATHON DETAIL
# ═══════════════════════════════════════════════════════════════

@router.get("/{hackathon_id}", status_code=status.HTTP_200_OK)
def get_hackathon_details(
    hackathon_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get full hackathon details including teams, rules, etc."""
    try:
        hackathon = foundry_service.get_hackathon_by_id(hackathon_id=hackathon_id)
        if not hackathon:
            return error_response(404, "Hackathon not found")

        return {"success": True, "hackathon": hackathon}

    except HTTPException:
        raise
    except Exception as e:
        return error_response(500, f"Failed to fetch hackathon: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# JOIN HACKATHON (QUICK)
# ═══════════════════════════════════════════════════════════════

@router.post("/{hackathon_id}/join", status_code=status.HTTP_200_OK)
def join_hackathon(
    hackathon_id: str,
    current_user: User = Depends(get_current_user),
):
    """Quick join — registers the user for the hackathon."""
    try:
        # Check if already registered
        is_registered = foundry_service.check_hackathon_registration(
            hackathon_id=hackathon_id, user_id=str(current_user.id)
        )
        if is_registered:
            return error_response(409, "You are already registered for this hackathon")

        # Register
        result = foundry_service.register_for_hackathon(
            hackathon_id=hackathon_id,
            user_id=str(current_user.id)
        )

        if result.get("status") == "error":
            return error_response(500, result.get("message", "Registration failed"))

        return {
            "success": True,
            "message": "Your team has successfully joined the hackathon.",
            "registrationId": result.get("registration_id")
        }

    except HTTPException:
        raise
    except Exception as e:
        return error_response(500, f"Join failed: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# REGISTER FOR HACKATHON (FULL FORM)
# ═══════════════════════════════════════════════════════════════

@router.post("/{hackathon_id}/register", status_code=status.HTTP_200_OK)
def register_for_hackathon(
    hackathon_id: str,
    payload: HackathonRegistrationRequest,
    current_user: User = Depends(get_current_user),
):
    """Full registration with form data."""
    try:
        # Validate rules agreement
        if not payload.agree_to_rules:
            return error_response(400, "You must agree to the rules to register")

        # Check if already registered
        is_registered = foundry_service.check_hackathon_registration(
            hackathon_id=hackathon_id, user_id=str(current_user.id)
        )
        if is_registered:
            return error_response(409, "You are already registered for this hackathon")

        # Register
        result = foundry_service.register_for_hackathon(
            hackathon_id=hackathon_id,
            user_id=str(current_user.id)
        )

        if result.get("status") == "error":
            return error_response(500, result.get("message", "Registration failed"))

        return {
            "success": True,
            "message": "Registration confirmed",
            "registrationId": result.get("registration_id"),
        }

    except HTTPException:
        raise
    except Exception as e:
        return error_response(500, f"Registration failed: {str(e)}")

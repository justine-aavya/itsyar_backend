from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from app.api.deps import get_current_user
from app.models.user import User
from app.integrations.palantir import foundry_service
from .schemas import HackathonRegistrationRequest

from .schemas import HackathonRegistrationRequest, SubmissionRequest

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
    

# ═══════════════════════════════════════════════════════════════
# TEAMS FOR A HACKATHON
# ═══════════════════════════════════════════════════════════════

@router.get("/{hackathon_id}/teams", status_code=status.HTTP_200_OK)
def get_hackathon_teams(
    hackathon_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get all teams for a hackathon."""
    try:
        teams = foundry_service._get_teams_for_hackathon(hackathon_id)
        return {"success": True, "teams": teams}

    except HTTPException:
        raise
    except Exception as e:
        return error_response(500, f"Failed to fetch teams: {str(e)}")


@router.post("/{hackathon_id}/teams", status_code=status.HTTP_201_CREATED)
def create_team(
    hackathon_id: str,
    current_user: User = Depends(get_current_user),
):
    """Create a team for a hackathon. (Pending: create_team action not available yet)"""
    return error_response(501, "Team creation is not yet available. Coming soon.")


# ═══════════════════════════════════════════════════════════════
# PROBLEM STATEMENT
# ═══════════════════════════════════════════════════════════════

@router.get("/{hackathon_id}/problem", status_code=status.HTTP_200_OK)
def get_hackathon_problem(
    hackathon_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get problem statement for a hackathon."""
    try:
        # Check hackathon status — only show if running/active
        hackathon = foundry_service.get_hackathon_by_id(hackathon_id)
        if not hackathon:
            return error_response(404, "Hackathon not found")

        status_val = str(hackathon.get("status", "")).lower()
        if status_val not in ("active", "open", "in progress", "running"):
            return error_response(403, "Problem statement is only available when hackathon is running")

        # TODO: Fetch from Foundry problem object when available
        return error_response(501, "Problem statements not yet available in Foundry")

    except HTTPException:
        raise
    except Exception as e:
        return error_response(500, f"Failed to fetch problem: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# SUBMIT SOLUTION
# ═══════════════════════════════════════════════════════════════



@router.post("/{hackathon_id}/submit", status_code=status.HTTP_200_OK)
def submit_solution(
    hackathon_id: str,
    payload: SubmissionRequest,
    current_user: User = Depends(get_current_user),
):
    """Submit solution for a hackathon."""
    try:
        result = foundry_service.submit_hackathon_solution(
            hackathon_id=hackathon_id,
            user_id=str(current_user.id),
            language=payload.language,
            code=payload.code,
            notes=payload.notes or "",
        )

        if result.get("status") == "error":
            return error_response(500, result.get("message", "Submission failed"))

        return {
            "success": True,
            "submission_id": result.get("submission_id"),
            "status": "PENDING",
            "message": "Submission received and queued for review.",
        }

    except HTTPException:
        raise
    except Exception as e:
        return error_response(500, f"Submission failed: {str(e)}")



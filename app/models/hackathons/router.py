from fastapi import APIRouter, Depends, HTTPException, Query, status

from pydantic import BaseModel

from typing import Optional



from app.api.deps import get_current_user, require_role

from app.models.user import User

import os

from app.integrations.palantir import foundry_service

from app.integrations.palantir.foundry_client import verify_foundry_credentials





router = APIRouter()



class EventRegistration(BaseModel):

    event_id: str



@router.get("/status")

def foundry_status():

    """Check if Foundry is responding or running into authentication blocks."""

    url = os.getenv("FOUNDRY_URL", "")

    client_id = os.getenv("FOUNDRY_CLIENT_ID", "")

    client_secret = os.getenv("FOUNDRY_CLIENT_SECRET", "")

   

    # Run the live network check matching your terminal diagnostics

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

            "message": f"Configuration error: Palantir rejected your keys. Details: {check['message']}"

        }



@router.get("/stats")

def platform_stats(current_user: User = Depends(require_role(["Admin", "Mentor"]))):

    try:

        return foundry_service.get_platform_stats()

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))



@router.get("/events")

def list_events(status_filter: Optional[str] = Query(None, alias="status"), current_user: User = Depends(get_current_user)):

    try:

        events = foundry_service.get_all_events(status_filter=status_filter)

        return {"ok": True, "events": events, "count": len(events)}

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"OSDK data retrieval failed: {str(e)}")



@router.get("/events/{event_id}")

def get_event(event_id: str, current_user: User = Depends(get_current_user)):

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

    try:

        challenges = foundry_service.get_challenges(event_id)

        return {"event_id": event_id, "challenges": challenges, "count": len(challenges)}

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))



@router.get("/tracks")

def list_tracks(current_user: User = Depends(get_current_user)):

    try:

        tracks = foundry_service.get_all_tracks()

        return {"tracks": tracks, "count": len(tracks)}

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))



@router.post("/events/{event_id}/enrol")

def enroll_in_event(event_id: str, current_user: User = Depends(require_role(["Student", "Participant"]))):

    try:

        result = foundry_service.register_for_event(event_id=event_id, user_id=str(current_user.id))

        if isinstance(result, dict) and result.get("status") == "error":

            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("message"))

        return {"ok": True, "data": result}

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Foundry Action Rejected: {str(e)}")
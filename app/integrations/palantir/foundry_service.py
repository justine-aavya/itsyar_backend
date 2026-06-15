from typing import Optional, List, Dict, Any
from app.integrations.palantir.foundry_client import (
    foundry_osdk, is_foundry_configured, get_mock_events, get_mock_tracks,
    flatten_osdk_object, apply_effective_status
)

def get_all_events(status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    if not is_foundry_configured():
        mock_data = get_mock_events()
        if status_filter:
            requested_statuses = [s.strip().upper() for s in status_filter.split(",")]
            return [e for e in mock_data if str(e.get("status")).upper() in requested_statuses]
        return mock_data
        
    try:
        client = foundry_osdk.get_client()
        osdk_events = client.ontology.objects.VanyarEvent.page(page_size=100)
        
        # response = client.api.v2.ontologies.Ontology.Object.list(
        #     ontology_rid=foundry_osdk.ontology_rid,
        #     object_type_api_name="VanyarEvent"  
        # )
        
        # Parse the incoming page entries
        events_list = []
        for obj in osdk_events:
            # Safely extract properties dictionary out of the OSDK data record node
            props = getattr(obj, "properties", obj)
            events_list.append({
                "userId": props.get("userId") or getattr(obj, "primary_key", {}).get("userId") or str(getattr(obj, "id", "")),
                "name": props.get("name", "Unnamed User"),
                "role": props.get("role", "Student"),
                "email": props.get("email", "")
            })
        
        if status_filter:
            requested_statuses = [s.strip().upper() for s in status_filter.split(",")]
            return [e for e in events_list if str(e.get("role")).upper() in requested_statuses]
            
        return events_list if events_list else get_mock_events()
        
    except Exception as e:
        print(f"[FOUNDRY ERROR] Live events fetch failed: {str(e)}. Falling back to mock data.")
        return get_mock_events()

def get_event_by_id(event_id: str) -> Optional[Dict[str, Any]]:
    if not is_foundry_configured():
        events = get_mock_events()
        return next((e for e in events if e["id"] == event_id), None)
        
    try:
        client = foundry_osdk.get_client()
        raw_event = client.ontology.objects.VanyarEvent.get(event_id)
        return apply_effective_status(flatten_osdk_object(raw_event))
    except Exception as e:
        print(f"[FOUNDRY ERROR] Fetching event {event_id} failed: {str(e)}")
        return None

def search_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    if not is_foundry_configured():
        return None
    try:
        client = foundry_osdk.get_client()
        results = client.ontology.objects.VanyarUser.filter(
            client.ontology.objects.VanyarUser.email == email.lower()
        ).page(page_size=1)
        if results:
            return flatten_osdk_object(results[0])
        return None
    except Exception as e:
        print(f"[FOUNDRY ERROR] Email object lookup failed: {str(e)}")
        return None

def get_all_tracks() -> List[Dict[str, Any]]:
    if not is_foundry_configured():
        return get_mock_tracks()
    try:
        client = foundry_osdk.get_client()
        raw_tracks = client.ontology.objects.VanyarTrack.page(page_size=50)
        return [flatten_osdk_object(item) for item in raw_tracks]
    except Exception as e:
        print(f"[FOUNDRY ERROR] Live tracks fetch failed: {str(e)}")
        return get_mock_tracks()

def register_for_event(event_id: str, user_id: str) -> Dict[str, Any]:
    if not is_foundry_configured():
        return {
            "status": "success",
            "message": f"Successfully registered for event {event_id} (Mock Confirmation)",
            "registration_id": "mock_reg_12345"
        }
    try:
        client = foundry_osdk.get_client()
        response = client.ontologies.Ontology.Object.list(
            ontology_rid=foundry_osdk.ontology_rid,
            object_type_api_name="VanyarTrack"  # 
        )
        tracks_list = []
        for obj in response.data:
            props = obj.properties
            tracks_list.append({
                "id": props.get("id") or obj.primary_key.get("id"),
                "name": props.get("name", "Unnamed Track"),
                "moduleCount": int(props.get("moduleCount", 0)),
                "description": props.get("description", "")
            })
            
        return tracks_list if tracks_list else get_mock_tracks()
    except Exception as e:
        print(f"[FOUNDRY ERROR] Live tracks fetch failed: {str(e)}. Falling back to mock data.")
        return get_mock_tracks()

def get_challenges(event_id: str) -> list:
    return [
        {"id": "ch_1", "title": "Predictive Logistics Model", "difficulty": "Hard"},
        {"id": "ch_2", "title": "Natural Language Document Parser", "difficulty": "Medium"}
    ]

def get_platform_stats() -> dict:
    return {"total_registrations": 16, "active_students": 10, "active_participants": 6, "completion_rate": "88%"}

def get_all_reviews() -> list:
    return [
        {"name": "Clara Vance", "role": "Student", "text": "The platform's deep integration with live datasets helped me land my job!"},
        {"name": "Marcus Wright", "role": "Participant", "text": "Incredibly smooth deployment workflows."}
    ]

def get_top_leaderboard(limit: int = 4) -> list:
    return [
        {"rank": 1, "name": "Alex Honnold", "pts": "2,450"},
        {"rank": 2, "name": "Sierra Blair", "pts": "2,210"},
        {"rank": 3, "name": "Clara Vance", "pts": "1,980"},
        {"rank": 4, "name": "Marcus Wright", "pts": "1,850"}
    ][:limit]


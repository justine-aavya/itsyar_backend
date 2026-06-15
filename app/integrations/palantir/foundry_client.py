import os
import time
from datetime import datetime
from typing import Any, Dict, Optional
from foundry_sdk import FoundryClient
from foundry_sdk import ConfidentialClientAuth

class FoundryOSDKManager:
    def __init__(self):
        self.url = os.getenv("FOUNDRY_URL")
        self.client_id = os.getenv("FOUNDRY_CLIENT_ID") or os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("FOUNDRY_CLIENT_SECRET") or os.getenv("CLIENT_SECRET") or os.getenv("foundry_client_secret")
        self.ontology_rid = os.getenv("FOUNDRY_ONTOLOGY_RID") or os.getenv("ONTOLOGY_RID") or os.getenv("foundry_ontology_rid")
        
        self._client: Optional[FoundryClient] = None
        self._token_expiry: float = 0.0

    def is_configured(self) -> bool:
        return all([self.url, self.client_id, self.client_secret, self.ontology_rid])

    def get_client(self) -> FoundryClient:
        if not self.is_configured():
            raise RuntimeError("Foundry credentials missing from environment parameters.")

        if self._client and time.time() < (self._token_expiry - 60):
            return self._client

        print("[FOUNDRY] Initializing client platform credentials flow...")
        clean_hostname = self.url.replace("https://", "").replace("http://", "").rstrip("/")

        auth_provider = ConfidentialClientAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=[
                "api:use-ontologies-read",
                "api:use-ontologies-write",
                "api:use-mediasets-read",
                "api:use-mediasets-write"
            ]
        )
        
        self._client = FoundryClient(
            auth=auth_provider,
            hostname=clean_hostname
        )
        
        self._token_expiry = time.time() + 3600
        return self._client


import requests
from typing import Dict, Any

def verify_foundry_credentials(
    foundry_url: str, 
    client_id: str, 
    client_secret: str
) -> Dict[str, Any]:
    """
    Pings the Palantir Multipass OAuth2 endpoint to verify if the 
    Client ID and Client Secret are active and responding.
    """
    # Ensure the URL is clean and points to the token endpoint
    base_url = foundry_url.strip().rstrip('/')
    token_url = f"{base_url}/multipass/api/oauth2/token"
    
    # Standard OAuth2 Client Credentials Payload
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    try:
        # Send a POST request to request an access token
        response = requests.post(token_url, data=payload, timeout=10)
        
        if response.status_code == 200:
            return {
                "status": "success",
                "connected": True,
                "message": "Credentials verified! Palantir Foundry responded successfully.",
                "details": response.json()  # Contains token metadata
            }
        elif response.status_code in [400, 401]:
            return {
                "status": "unauthorized",
                "connected": False,
                "message": "Palantir responded, but Client ID or Client Secret is invalid.",
                "status_code": response.status_code,
                "error_details": response.text
            }
        else:
            return {
                "status": "error",
                "connected": False,
                "message": f"Palantir server responded with an unexpected error status.",
                "status_code": response.status_code,
                "error_details": response.text
            }
            
    except requests.exceptions.ConnectionError:
        return {
            "status": "network_failure",
            "connected": False,
            "message": f"Could not reach Palantir at '{base_url}'. Check the URL or your network connection."
        }
    except requests.exceptions.Timeout:
        return {
            "status": "timeout",
            "connected": False,
            "message": "The connection attempt timed out while waiting for Palantir to respond."
        }
    except Exception as e:
        return {
            "status": "exception",
            "connected": False,
            "message": f"An unexpected system error occurred: {str(e)}"
        }

foundry_osdk = FoundryOSDKManager()

def is_foundry_configured() -> bool:
    return foundry_osdk.is_configured()



def flatten_osdk_object(obj: Any) -> Dict[str, Any]:
    if not obj:
        return {}
    if hasattr(obj, "to_dict"):
        data = obj.to_dict()
    elif isinstance(obj, dict):
        data = obj.copy()
    else:
        try:
            data = dict(obj)
        except (TypeError, ValueError):
            return {}

    primary_key = (
        data.pop("primaryKey", None) or 
        data.pop("primary_key", None) or 
        data.pop("__primaryKey__", None) or
        data.pop("id", None)
    )
    if primary_key is not None:
        data["id"] = primary_key
        
    data.pop("__apiName__", None)
    data.pop("__rid__", None)
    return data

def apply_effective_status(event_data: dict) -> dict:
    if not isinstance(event_data, dict):
        return event_data

    stored_status = str(event_data.get("status", "")).upper()
    if stored_status in ["DRAFT", "CANCELLED"]:
        return event_data

    if stored_status == "UPCOMING":
        stored_status = "PUBLISHED"

    start_date = event_data.get("startDate") or event_data.get("start_date")
    end_date = event_data.get("endDate") or event_data.get("end_date")
    
    if start_date and end_date:
        try:
            now = datetime.utcnow()
            start = datetime.fromisoformat(str(start_date).replace("Z", ""))
            end = datetime.fromisoformat(str(end_date).replace("Z", ""))
            
            if now > end:
                event_data["status"] = "COMPLETED"
            elif start <= now <= end:
                event_data["status"] = "ACTIVE"
            else:
                event_data["status"] = stored_status
        except ValueError:
            event_data["status"] = stored_status
    else:
        event_data["status"] = stored_status
        
    event_data["title"] = event_data.get("title") or event_data.get("name")
    return event_data

def get_mock_events() -> list:
    return [
        {
            "id": "evt_mock_1",
            "title": "Orion Hackathon Alpha",
            "description": "Enterprise-wide data streaming simulation bracket challenge.",
            "status": "ACTIVE",
            "startDate": "2026-01-01T00:00:00Z",
            "endDate": "2026-12-31T23:59:59Z",
            "eventType": "Analytical",
            "orgId": "demo-org"
        },
        {
            "id": "evt_mock_2",
            "title": "Vanyar Code Sprint Beta",
            "description": "Algorithmic execution matrix optimization sprint.",
            "status": "PUBLISHED",
            "startDate": "2026-08-01T00:00:00Z",
            "endDate": "2026-08-15T23:59:59Z",
            "eventType": "Algorithmic",
            "orgId": "demo-org"
        },
        {
            "id": "evt_mock_3",
            "title": "Legacy Data Engine Challenge",
            "description": "Historical predictive model training challenge.",
            "status": "COMPLETED",
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2025-01-10T23:59:59Z",
            "eventType": "Predictive",
            "orgId": "demo-org"
        }
    ]

def get_mock_tracks() -> list:
    return [
        {
            "id": "track_mock_1",
            "name": "Artificial Intelligence & ML Graphs",
            "moduleCount": 8,
            "description": "Deep-dive neural network architecture modeling."
        },
        {
            "id": "track_mock_2",
            "name": "Enterprise Cloud Architecture & DevOps",
            "moduleCount": 5,
            "description": "High-availability deployment management setups."
        }
    ]
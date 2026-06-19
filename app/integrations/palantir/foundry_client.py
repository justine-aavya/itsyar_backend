# app/integrations/palantir/foundry_client.py
import os
import time
from typing import Any, Dict, Optional

import requests
from training_and_hackathon_sdk import FoundryClient, ConfidentialClientAuth


class FoundryOSDKManager:
    def __init__(self):
        self.url = os.getenv("FOUNDRY_URL")
        self.client_id = os.getenv("FOUNDRY_CLIENT_ID")
        self.client_secret = os.getenv("FOUNDRY_CLIENT_SECRET")
        self.ontology_rid = os.getenv("FOUNDRY_ONTOLOGY_RID")

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


def verify_foundry_credentials(
    foundry_url: str,
    client_id: str,
    client_secret: str
) -> Dict[str, Any]:
    """
    Pings the Palantir Multipass OAuth2 endpoint to verify if the
    Client ID and Client Secret are active and responding.
    """
    base_url = foundry_url.strip().rstrip('/')
    token_url = f"{base_url}/multipass/api/oauth2/token"

    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    try:
        response = requests.post(token_url, data=payload, timeout=10)

        if response.status_code == 200:
            return {
                "status": "success",
                "connected": True,
                "message": "Credentials verified! Palantir Foundry responded successfully.",
                "details": response.json()
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
                "message": "Palantir server responded with an unexpected error status.",
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


# ─── Module-level singleton ───────────────────────────────────────────────────
foundry_osdk = FoundryOSDKManager()


def is_foundry_configured() -> bool:
    return foundry_osdk.is_configured()

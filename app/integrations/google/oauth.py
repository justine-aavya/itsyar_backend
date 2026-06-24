# app/integrations/google/oauth.py
"""
Google OAuth helper — verifies Google ID tokens.
Used by the auth router to authenticate Google Sign-In users.
"""

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.core.config import settings
from typing import Optional, Dict


def verify_google_token(token: str) -> Optional[Dict[str, str]]:
    """
    Verify a Google ID token and extract user info.
    
    Args:
        token: The Google ID token from frontend
        
    Returns:
        Dict with email, name, sub (Google user ID) or None if invalid
    """
    try:
        # Verify token with Google's servers
        google_info = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )

        # Extract user info
        email = google_info.get("email", "").strip().lower()
        name = google_info.get("name", "")
        sub = google_info.get("sub", "")  # Google's unique user ID

        if not email:
            return None

        return {
            "email": email,
            "name": name,
            "sub": sub,
            "picture": google_info.get("picture", ""),
        }

    except ValueError:
        # Invalid token
        return None
    except Exception:
        return None

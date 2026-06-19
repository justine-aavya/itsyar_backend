# from fastapi import FastAPI, Depends
# from fastapi.middleware.cors import CORSMiddleware

# from app.db.session import engine
# from app.db.base import Base

# import os
# from app.integrations.palantir.foundry_client import verify_foundry_credentials

# from app.api.router import api_router
# from app.api.deps import get_current_user
# from app.models.user import User
# from app.models.auth.schemas import UserResponse



# Base.metadata.create_all(bind=engine)

# app = FastAPI(title="itsyar Architecture Engine", version="3.0.0", docs_url="/docs")

# @app.on_event("startup")
# def diagnostic_check():
#     print("\n[DIAGNOSTIC] Testing Palantir Foundry Client Credentials...")
#     # Pull variables directly out of your current .env setup
#     url = os.getenv("FOUNDRY_URL", "https://your-company.palantirfoundry.com")
#     client_id = os.getenv("FOUNDRY_CLIENT_ID")
#     client_secret = os.getenv("FOUNDRY_CLIENT_SECRET")

#     if not client_id or not client_secret:
#         print("[DIAGNOSTIC WARNING] Missing credentials in .env file. Skipping check.")
#         return

#     result = verify_foundry_credentials(url, client_id, client_secret)

#     if result["connected"]:
#         print(f"✅ {result['message']}\n")
#     else:
#         print(f"❌ CONNECTION FAILED: {result['message']}")
#         print(f"Details: {result.get('error_details', 'N/A')}\n")

# app.add_middleware(
#     CORSMiddleware,
#     #allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173", "http://192.168.1.183:8000"],
#     allow_origins=["*"],  # Allow all origins for development; restrict in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Core Global Prefix Mount Point
# app.include_router(api_router, prefix="/api")

# @app.get("/api/auth/me", response_model=UserResponse, tags=["Authentication Layer"])
# def get_me(current_user: User = Depends(get_current_user)):
#     return UserResponse.model_validate(current_user)

# @app.get("/", tags=["System Diagnostics"])
# def system_health_status():
#     return {"status": "healthy, iysyar is running."} 


import os
import re
import json
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.db.session import engine
from app.db.base import Base

from app.integrations.palantir.foundry_client import verify_foundry_credentials

from app.api.router import api_router
from app.api.deps import get_current_user
from app.models.user import User
from app.models.auth.schemas import UserResponse


Base.metadata.create_all(bind=engine)

app = FastAPI(title="itsyar Architecture Engine", version="3.0.0", docs_url="/docs")


# ═══════════════════════════════════════════════════════════════
# CAMELCASE RESPONSE MIDDLEWARE
# Converts all JSON response keys from snake_case → camelCase
# so frontend (JavaScript) receives consistent camelCase keys.
# ═══════════════════════════════════════════════════════════════

def _to_camel_case(snake_str: str) -> str:
    parts = snake_str.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])


def _convert_keys(obj):
    if isinstance(obj, dict):
        return {_to_camel_case(k): _convert_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_keys(item) for item in obj]
    return obj


class CamelCaseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # Skip conversion for docs/openapi paths
        path = request.url.path
        if path in ("/docs", "/redoc", "/openapi.json"):
            return response

        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response

        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        try:
            data = json.loads(body)
            camel_data = _convert_keys(data)
            new_body = json.dumps(camel_data).encode()

            # Build new headers WITHOUT Content-Length (let Starlette recalculate)
            new_headers = {
                k: v for k, v in response.headers.items()
                if k.lower() != "content-length"
            }

            return Response(
                content=new_body,
                status_code=response.status_code,
                headers=new_headers,
                media_type="application/json"
            )
        except (json.JSONDecodeError, Exception):
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers)
            )




# ═══════════════════════════════════════════════════════════════
# STARTUP DIAGNOSTIC
# ═══════════════════════════════════════════════════════════════

@app.on_event("startup")
def diagnostic_check():
    print("\n[DIAGNOSTIC] Testing Palantir Foundry Client Credentials...")
    url = os.getenv("FOUNDRY_URL", "https://your-company.palantirfoundry.com")
    client_id = os.getenv("FOUNDRY_CLIENT_ID")
    client_secret = os.getenv("FOUNDRY_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("[DIAGNOSTIC WARNING] Missing credentials in .env file. Skipping check.")
        return

    result = verify_foundry_credentials(url, client_id, client_secret)

    if result["connected"]:
        print(f"✅ {result['message']}\n")
    else:
        print(f"❌ CONNECTION FAILED: {result['message']}")
        print(f"Details: {result.get('error_details', 'N/A')}\n")


# ═══════════════════════════════════════════════════════════════
# MIDDLEWARE STACK (order matters: CORS first, then CamelCase)
# ═══════════════════════════════════════════════════════════════

app.add_middleware(CamelCaseMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════

app.include_router(api_router, prefix="/api")


@app.get("/api/auth/me", response_model=UserResponse, tags=["Authentication Layer"])
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@app.get("/", tags=["System Diagnostics"])
def system_health_status():
    return {"status": "healthy, itsyar is running."}

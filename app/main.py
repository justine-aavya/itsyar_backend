import os
import re
import json
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from fastapi import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


from app.db.session import engine
from app.db.base import Base

from app.integrations.palantir.foundry_client import verify_foundry_credentials

from app.api.router import api_router
from app.api.deps import get_current_user
from app.models.user import User
from app.models.auth.schemas import UserResponse

from app.core.config import settings
print(f"[STARTUP] ACCESS_TOKEN_EXPIRE_MINUTES = {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")


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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):

    # Get the first error message (most relevant to user)
    errors = exc.errors()
    if errors:
        first_error = errors[0]
        field = first_error.get("loc", [])[-1]  # e.g., "confirmPassword"
        message = first_error.get("msg", "Validation failed")

        # Clean up Pydantic's message format
        if message.startswith("Value error, "):
            message = message.replace("Value error, ", "")

        friendly_message = f"{message}" if field == "__root__" else f"{field}: {message}"
    else:
        friendly_message = "Invalid request data"

    return JSONResponse(
        status_code=422,
        content={"error": {"data": {"message": friendly_message}}}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"data": {"message": exc.detail}}}
    )

# ═══════════════════════════════════════════════════════════════
# MIDDLEWARE STACK (order matters: CORS first, then CamelCase)
# ═══════════════════════════════════════════════════════════════

app.add_middleware(CamelCaseMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
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

# ═══════════════════════════════════════════════════════════════
# video streaming (update this to use a proper video streaming solution in production)
# ═══════════════════════════════════════════════════════════════

app.mount("/static", StaticFiles(directory="static"), name="static")

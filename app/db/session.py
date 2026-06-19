# # session.py
# import os
# from typing import Generator
# from training_and_hackathon_sdk import FoundryClient, ConfidentialClientAuth
# from app.core.config import settings

# print("⚡ [SYSTEM] Initializing unified Palantir OSDK connection gateway...")

# # 1. Clean and parse the raw URL to extract a clean hostname domain
# raw_url = settings.FOUNDRY_URL or os.getenv("FOUNDRY_URL", "")
# clean_hostname = raw_url.replace("https://", "").replace("http://", "")
# if "/multipass" in clean_hostname:
#     clean_hostname = clean_hostname.split("/multipass")[0]
# clean_hostname = clean_hostname.rstrip("/")

# # 2. Gather fallbacks for Client ID and Secret from configurations
# client_id = settings.FOUNDRY_CLIENT_ID or settings.CLIENT_ID
# client_secret = settings.FOUNDRY_CLIENT_SECRET or settings.CLIENT_SECRET or settings.foundry_client_secret

# # 3. Instantiate a long-lived, reusable authentication context session
# # This handles OAuth2 token refreshing automatically behind the scenes
# auth_client = ConfidentialClientAuth(
#     client_id=client_id,
#     client_secret=client_secret,
#     should_refresh=True,
# )

# # 4. Initialize the global shared client instance
# foundry_singleton_client = FoundryClient(auth=auth_client, hostname=clean_hostname)
# print("✅ [SYSTEM] Global Palantir OSDK Client Session Pooled Successfully.")

# # ─────────────────────────────────────────────────────────────
# #  THE REPLACEMENT FUNCTION: get_foundry dependency generator
# # ─────────────────────────────────────────────────────────────
# def get_foundry() -> Generator[FoundryClient, None, None]:
#     """
#     FastAPI Dependency injection provider. Yields the active, authenticated 
#     Palantir OSDK client session to routers and security filters.
#     """
#     try:
#         yield foundry_singleton_client
#     finally:
#         # Palantir connection pools handle their own cleanup automatically; 
#         # no manual connection closing or session clearing is required here.
#         pass



# # Important Note Regarding get_foundry
# # 💡 Architectural Note: > Unlike your old get_db() function which had to run .close() on every request to prevent running out of database connections, the new get_foundry() instance uses an internal, thread-safe network pool wrapper managed by the OSDK.
# # When your API routers or deps.py ask for Depends(get_foundry), they instantly receive a reference to this pre-authenticated hot connection pool. This gives your FastAPI backend near-zero latency overhead when initiating dynamic stream queries (.take() or .where()) directly into the cloud.

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

from app.core.config import settings



# Setup database engine

engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# ─────────────────────────────────────────────────────────────

#  THE MISSING FUNCTION: get_db dependency generator

# ─────────────────────────────────────────────────────────────

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close() 


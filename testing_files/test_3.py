# test_video_fetch.py — run with: python test_video_fetch.py

import os
import requests
from dotenv import load_dotenv
load_dotenv()

FOUNDRY_URL = os.getenv("FOUNDRY_URL", "").rstrip("/")
CLIENT_ID = os.getenv("FOUNDRY_CLIENT_ID")
CLIENT_SECRET = os.getenv("FOUNDRY_CLIENT_SECRET")

print("=" * 60)
print("STEP 1: Get OAuth Token")
print("=" * 60)

token_resp = requests.post(
    f"{FOUNDRY_URL}/multipass/api/oauth2/token",
    data={
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    },
    timeout=10
)

print(f"  Token endpoint status: {token_resp.status_code}")
print(f"  Response: {token_resp.text[:300]}")

token = token_resp.json().get("access_token")

if not token:
    print("❌ No token received. Check CLIENT_ID and CLIENT_SECRET.")
    exit()

print(f"  ✅ Token received: {token[:20]}...")

print("\n" + "=" * 60)
print("STEP 2: Fetch a course to get video URL")
print("=" * 60)

from app.integrations.palantir.foundry_service import get_single_course
from contextlib import contextmanager
try:
    from foundry_sdk_runtime import AllowBetaFeatures
except ImportError:
    @contextmanager
    def AllowBetaFeatures():
        yield

COURSE_ID = "1"  # <-- change to a real course ID

course = get_single_course(COURSE_ID)
if not course:
    print(f"❌ Course {COURSE_ID} not found")
    exit()

video_url = course.get("course_url1")
print(f"  course_url1 = {video_url}")

if not video_url:
    print("❌ No video URL on this course object")
    exit()

print("\n" + "=" * 60)
print("STEP 3: Fetch video with token")
print("=" * 60)

video_resp = requests.get(
    video_url,
    headers={"Authorization": f"Bearer {token}"},
    stream=True,
    timeout=15
)

print(f"  Video fetch status: {video_resp.status_code}")
print(f"  Content-Type: {video_resp.headers.get('content-type')}")
print(f"  Content-Length: {video_resp.headers.get('content-length')}")

if video_resp.status_code == 200:
    print("  ✅ Video accessible!")
elif "html" in video_resp.headers.get("content-type", ""):
    print("  ❌ Got login page — token not valid for this resource")
else:
    print(f"  ❌ Failed: {video_resp.text[:200]}")

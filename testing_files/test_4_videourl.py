import requests
import re
import os
from dotenv import load_dotenv
load_dotenv()

FOUNDRY_URL = os.getenv("FOUNDRY_URL", "").rstrip("/")
CLIENT_ID = os.getenv("FOUNDRY_CLIENT_ID")
CLIENT_SECRET = os.getenv("FOUNDRY_CLIENT_SECRET")

# Get token
token_resp = requests.post(f"{FOUNDRY_URL}/multipass/api/oauth2/token", data={
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
}, timeout=10)
token = token_resp.json().get("access_token")

# Fetch the preview-app HTML
RID = "ri.blobster.main.video.7fd1176e-db42-47ad-b611-f5e65a3a9afb"
url = f"{FOUNDRY_URL}/workspace/preview-app/{RID}"

resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
html = resp.text

print(f"Status: {resp.status_code}")
print(f"HTML length: {len(html)} chars")
print("\n" + "=" * 60)
print("FULL HTML RESPONSE:")
print("=" * 60)
print(html)

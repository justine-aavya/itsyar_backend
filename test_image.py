# # test_image.py
# import os
# from dotenv import load_dotenv
# load_dotenv()

# from app.integrations.palantir.foundry_client import foundry_osdk
# try:
#     from foundry_sdk_runtime import AllowBetaFeatures
# except ImportError:
#     from contextlib import contextmanager
#     @contextmanager
#     def AllowBetaFeatures():
#         yield

# COURSE_ID = 1

# with AllowBetaFeatures():
#     client = foundry_osdk.get_client()
#     course_obj = client.ontology.objects.Courses.get(COURSE_ID)

#     # Check the image property
#     img = course_obj.image
#     print(f"Type: {type(img)}")
#     print(f"Has .get_media_content(): {hasattr(img, 'get_media_content')}")

#     # Try reading image bytes
#     if hasattr(img, 'get_media_content'):
#         content = img.get_media_content().read()
#         print(f"✅ Got {len(content)} bytes")
#         print(f"First 4 bytes: {content[:4]}")  # JPEG starts with b'\xff\xd8\xff'
#         with open("test_thumbnail.jpg", "wb") as f:
#             f.write(content)
#         print("Saved to test_thumbnail.jpg — open it to verify!")
#     else:
#         print(f"❌ Not a media property. Value: {img}")
###################################################################################################

# # test_thumbnail_api.py
# import os, requests, json
# from dotenv import load_dotenv
# load_dotenv()

# FOUNDRY_URL = os.getenv("FOUNDRY_URL", "").rstrip("/")
# CLIENT_ID = os.getenv("FOUNDRY_CLIENT_ID")
# CLIENT_SECRET = os.getenv("FOUNDRY_CLIENT_SECRET")

# # Get token
# token_resp = requests.post(f"{FOUNDRY_URL}/multipass/api/oauth2/token", data={
#     "grant_type": "client_credentials",
#     "client_id": CLIENT_ID,
#     "client_secret": CLIENT_SECRET,
# }, timeout=10)
# token = token_resp.json().get("access_token")
# print(f"Token: {token[:20]}...")

# # Media reference details
# MEDIA_SET_RID = "ri.mio.main.media-set.63c42edb-43ee-415a-acc8-348587ab934b"
# MEDIA_ITEM_RID = "ri.mio.main.media-item.019ef316-a7f8-72d4-a068-97b008d7cba0"
# VIEW_RID = "ri.mio.main.view.823e45db-8722-47a9-895f-5b1d63fd0594"

# # Try different API paths
# urls_to_try = [
#     f"{FOUNDRY_URL}/api/v1/mediasets/{MEDIA_SET_RID}/items/{MEDIA_ITEM_RID}/content",
#     f"{FOUNDRY_URL}/api/v2/mediasets/{MEDIA_SET_RID}/items/{MEDIA_ITEM_RID}/content",
#     f"{FOUNDRY_URL}/api/v1/media-sets/{MEDIA_SET_RID}/items/{MEDIA_ITEM_RID}/content",
#     f"{FOUNDRY_URL}/api/v2/media-sets/{MEDIA_SET_RID}/items/{MEDIA_ITEM_RID}/content",
#     f"{FOUNDRY_URL}/api/v1/mediasets/{MEDIA_SET_RID}/views/{VIEW_RID}/items/{MEDIA_ITEM_RID}/content",
#     f"{FOUNDRY_URL}/api/v2/mediasets/{MEDIA_SET_RID}/views/{VIEW_RID}/items/{MEDIA_ITEM_RID}/content",
#     f"{FOUNDRY_URL}/mio/api/media-sets/{MEDIA_SET_RID}/items/{MEDIA_ITEM_RID}/content",
#     f"{FOUNDRY_URL}/api/v1/mio/media-sets/{MEDIA_SET_RID}/items/{MEDIA_ITEM_RID}/content",
# ]

# for url in urls_to_try:
#     resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
#     content_type = resp.headers.get("content-type", "")
#     print(f"[{resp.status_code}] {content_type[:30]:30s} → {url.replace(FOUNDRY_URL, '')}")
    
#     if resp.status_code == 200 and "image" in content_type:
#         print(f"    ✅ FOUND IT! Saving...")
#         with open("test_thumbnail.jpg", "wb") as f:
#             f.write(resp.content)
#         print(f"    Saved to test_thumbnail.jpg ({len(resp.content)} bytes)")
#         break

###################################################################################################

# # test_thumbnail_400.py
# import os, requests
# from dotenv import load_dotenv
# load_dotenv()

# FOUNDRY_URL = os.getenv("FOUNDRY_URL", "").rstrip("/")
# CLIENT_ID = os.getenv("FOUNDRY_CLIENT_ID")
# CLIENT_SECRET = os.getenv("FOUNDRY_CLIENT_SECRET")

# token_resp = requests.post(f"{FOUNDRY_URL}/multipass/api/oauth2/token", data={
#     "grant_type": "client_credentials",
#     "client_id": CLIENT_ID,
#     "client_secret": CLIENT_SECRET,
# }, timeout=10)
# token = token_resp.json().get("access_token")

# MEDIA_SET_RID = "ri.mio.main.media-set.63c42edb-43ee-415a-acc8-348587ab934b"
# MEDIA_ITEM_RID = "ri.mio.main.media-item.019ef316-a7f8-72d4-a068-97b008d7cba0"

# # The one that returned 400 — check the error body
# url = f"{FOUNDRY_URL}/api/v2/mediasets/{MEDIA_SET_RID}/items/{MEDIA_ITEM_RID}/content"
# resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)

# print(f"Status: {resp.status_code}")
# print(f"Response body: {resp.text}")

# # Also try without /content
# url2 = f"{FOUNDRY_URL}/api/v2/mediasets/{MEDIA_SET_RID}/items/{MEDIA_ITEM_RID}"
# resp2 = requests.get(url2, headers={"Authorization": f"Bearer {token}"}, timeout=10)
# print(f"\nWithout /content:")
# print(f"Status: {resp2.status_code}")
# print(f"Response body: {resp2.text[:500]}")

# # Try just listing items in the media set
# url3 = f"{FOUNDRY_URL}/api/v2/mediasets/{MEDIA_SET_RID}/items"
# resp3 = requests.get(url3, headers={"Authorization": f"Bearer {token}"}, timeout=10)
# print(f"\nList items:")
# print(f"Status: {resp3.status_code}")
# print(f"Response body: {resp3.text[:500]}")
##############################################################################################################3


# # test_thumbnail_preview.py
# import os, requests
# from dotenv import load_dotenv
# load_dotenv()

# FOUNDRY_URL = os.getenv("FOUNDRY_URL", "").rstrip("/")
# CLIENT_ID = os.getenv("FOUNDRY_CLIENT_ID")
# CLIENT_SECRET = os.getenv("FOUNDRY_CLIENT_SECRET")

# token_resp = requests.post(f"{FOUNDRY_URL}/multipass/api/oauth2/token", data={
#     "grant_type": "client_credentials",
#     "client_id": CLIENT_ID,
#     "client_secret": CLIENT_SECRET,
# }, timeout=10)
# token = token_resp.json().get("access_token")

# MEDIA_SET_RID = "ri.mio.main.media-set.63c42edb-43ee-415a-acc8-348587ab934b"
# MEDIA_ITEM_RID = "ri.mio.main.media-item.019ef316-a7f8-72d4-a068-97b008d7cba0"

# url = f"{FOUNDRY_URL}/api/v2/mediasets/{MEDIA_SET_RID}/items/{MEDIA_ITEM_RID}/content"

# # Try different preview headers
# preview_headers = [
#     {"Authorization": f"Bearer {token}", "Preview": "true"},
#     {"Authorization": f"Bearer {token}", "X-Feature-Preview": "true"},
#     {"Authorization": f"Bearer {token}", "Foundry-Preview": "true"},
#     {"Authorization": f"Bearer {token}", "X-Preview": "true"},
#     {"Authorization": f"Bearer {token}", "X-Api-Preview": "true"},
# ]

# for headers in preview_headers:
#     extra_key = [k for k in headers.keys() if k != "Authorization"][0]
#     resp = requests.get(url, headers=headers, timeout=10)
#     content_type = resp.headers.get("content-type", "")
#     print(f"[{resp.status_code}] {extra_key}: {headers[extra_key]} → {content_type[:30]}")
    
#     if resp.status_code == 200:
#         print(f"    ✅ FOUND IT! Header: {extra_key}")
#         with open("test_thumbnail.jpg", "wb") as f:
#             f.write(resp.content)
#         print(f"    Saved ({len(resp.content)} bytes)")
#         break
#     elif resp.status_code != 400:
#         print(f"    Response: {resp.text[:200]}")
######################################################################################################################3

# # test_thumbnail_ontology.py
# import os, requests
# from dotenv import load_dotenv
# load_dotenv()

# FOUNDRY_URL = os.getenv("FOUNDRY_URL", "").rstrip("/")
# CLIENT_ID = os.getenv("FOUNDRY_CLIENT_ID")
# CLIENT_SECRET = os.getenv("FOUNDRY_CLIENT_SECRET")
# ONTOLOGY_RID = "ri.ontology.main.ontology.2b524aaa-b15b-49c6-9b69-353f71badbaf"

# token_resp = requests.post(f"{FOUNDRY_URL}/multipass/api/oauth2/token", data={
#     "grant_type": "client_credentials",
#     "client_id": CLIENT_ID,
#     "client_secret": CLIENT_SECRET,
# }, timeout=10)
# token = token_resp.json().get("access_token")

# # Try Ontology media API for the image property
# urls = [
#     f"{FOUNDRY_URL}/api/v2/ontologies/{ONTOLOGY_RID}/objects/Courses/1/media/image/content",
#     f"{FOUNDRY_URL}/api/v2/ontologies/{ONTOLOGY_RID}/objects/Courses/1/media/image",
#     f"{FOUNDRY_URL}/api/v1/ontologies/{ONTOLOGY_RID}/objects/Courses/1/media/image/content",
# ]

# for url in urls:
#     resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)
#     ct = resp.headers.get("content-type", "")
#     print(f"[{resp.status_code}] {ct[:30]} → {url.replace(FOUNDRY_URL, '')}")
#     if resp.status_code == 200 and "image" in ct:
#         with open("test_thumbnail.jpg", "wb") as f:
#             f.write(resp.content)
#         print(f"    ✅ Got {len(resp.content)} bytes! Saved to test_thumbnail.jpg")
#         break
#     elif resp.status_code != 404:
#         print(f"    Body: {resp.text[:200]}")

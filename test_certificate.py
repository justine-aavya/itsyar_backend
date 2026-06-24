# test_certificate.py
import os
from dotenv import load_dotenv
load_dotenv()

from app.integrations.palantir.foundry_client import foundry_osdk
try:
    from foundry_sdk_runtime import AllowBetaFeatures
except ImportError:
    from contextlib import contextmanager
    @contextmanager
    def AllowBetaFeatures():
        yield

COURSE_ID = 1

with AllowBetaFeatures():
    client = foundry_osdk.get_client()
    course_obj = client.ontology.objects.Courses.get(COURSE_ID)

    cert = course_obj.certificate
    print(f"Type: {type(cert)}")
    print(f"Value: {cert}")
    print(f"Has .get_media_content(): {hasattr(cert, 'get_media_content')}")

    if hasattr(cert, 'get_media_content'):
        content = cert.get_media_content().read()
        print(f"✅ Got {len(content)} bytes")
        print(f"First 4 bytes: {content[:4]}")  # PNG starts with b'\x89PNG'
        with open("test_certificate.png", "wb") as f:
            f.write(content)
        print("Saved to test_certificate.png")
    else:
        print("❌ Not a Media property — same issue as image was before")
        print("   Ask Foundry engineer to change 'certificate' to a Media type property")

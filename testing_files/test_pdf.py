# # test_pdf.py — run with: python test_pdf.py

# import os
# from dotenv import load_dotenv
# load_dotenv()

# from app.integrations.palantir.foundry_client import foundry_osdk, is_foundry_configured
# from contextlib import contextmanager

# try:
#     from foundry_sdk_runtime import AllowBetaFeatures
# except ImportError:
#     @contextmanager
#     def AllowBetaFeatures():
#         yield


# COURSE_ID = 1  # <-- change to a real course ID

# print("=" * 60)
# print(f"TESTING PDF RETRIEVAL FOR COURSE {COURSE_ID}")
# print("=" * 60)

# print(f"\n[1] Foundry configured: {is_foundry_configured()}")

# # Everything must be INSIDE AllowBetaFeatures
# with AllowBetaFeatures():
#     # Step 2: Get course object
#     print(f"\n[2] Fetching course object...")
#     client = foundry_osdk.get_client()
#     course_obj = client.ontology.objects.Courses.get(COURSE_ID)
#     print(f"    Course found: {course_obj is not None}")

#     # Step 3: Check media property
#     print(f"\n[3] Checking course_resources1 property...")
#     prop = course_obj.course_resources1
#     print(f"    Type: {type(prop)}")
#     print(f"    Has .read(): {hasattr(prop, 'read')}")

#     # Step 4: Try reading PDF content
#     print(f"\n[4] Attempting to read PDF bytes...")
#     try:
#         if hasattr(prop, 'read'):
#             content = prop.read()
#             print(f"    ✅ SUCCESS! Got {len(content)} bytes")
#             print(f"    First 4 bytes: {content[:4]}")  # Should be b'%PDF'

#             with open("test_output.pdf", "wb") as f:
#                 f.write(content)
#             print(f"    Saved to test_output.pdf — open it to verify!")
#         elif prop is not None:
#             print(f"    Value: {str(prop)[:200]}")
#             print("    ❌ Not a readable media property")
#         else:
#             print("    ❌ Property is None (no PDF uploaded for this course)")

#     except Exception as e:
#         print(f"    ❌ FAILED: {str(e)}")

# print("\n" + "=" * 60)
# print("DONE")
# print("=" * 60)

#########################################################################################################
# # test_pdf_methods.py

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
#     media = course_obj.course_resources1

#     print(f"Type: {type(media)}")
#     print(f"\nAll attributes/methods:")
#     for attr in sorted(dir(media)):
#         if not attr.startswith('_'):
#             try:
#                 val = getattr(media, attr)
#                 val_type = type(val).__name__
#                 print(f"  {attr} ({val_type}) = {repr(val)[:100]}")
#             except Exception as e:
#                 print(f"  {attr} = [ERROR: {e}]")

#################################################################################################

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
#     media = course_obj.course_resources1

#     print("Attempting .get_media_content()...")
#     content = media.get_media_content()

#     print(f"Type of result: {type(content)}")
#     print(f"Has .read(): {hasattr(content, 'read')}")
#     print(f"Has .content: {hasattr(content, 'content')}")

#     # Try to get bytes
#     if isinstance(content, bytes):
#         print(f"✅ Got {len(content)} bytes directly")
#         print(f"First 4 bytes: {content[:4]}")
#         with open("test_output.pdf", "wb") as f:
#             f.write(content)
#         print("Saved to test_output.pdf")
#     elif hasattr(content, 'read'):
#         data = content.read()
#         print(f"✅ Got {len(data)} bytes via .read()")
#         print(f"First 4 bytes: {data[:4]}")
#         with open("test_output.pdf", "wb") as f:
#             f.write(data)
#         print("Saved to test_output.pdf")
#     elif hasattr(content, 'content'):
#         data = content.content
#         print(f"✅ Got {len(data)} bytes via .content")
#         print(f"First 4 bytes: {data[:4]}")
#         with open("test_output.pdf", "wb") as f:
#             f.write(data)
#         print("Saved to test_output.pdf")
#     else:
#         print(f"Result value: {repr(content)[:500]}")
#         print(f"Dir: {[a for a in dir(content) if not a.startswith('_')]}")

################################################################################################3

# test_pdf_endpoint.py

import os
from dotenv import load_dotenv
load_dotenv()

from app.integrations.palantir.foundry_service import get_course_pdf_content

COURSE_ID = "1"

print(f"Testing PDF retrieval for course {COURSE_ID}...")

content, content_type = get_course_pdf_content(COURSE_ID)

if content:
    print(f"✅ SUCCESS!")
    print(f"   Content type: {content_type}")
    print(f"   Size: {len(content)} bytes")
    print(f"   First 4 bytes: {content[:4]}")  # Should be b'%PDF'
    
    # Save to verify
    with open("test_output.pdf", "wb") as f:
        f.write(content)
    print(f"   Saved to test_output.pdf — open it to verify!")
else:
    print("❌ FAILED: No content returned")

# # test_video_property.py

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

#     # Step 1: List ALL properties on the course object
#     print("=" * 60)
#     print("ALL PROPERTIES ON COURSES OBJECT:")
#     print("=" * 60)
#     for attr in sorted(dir(course_obj)):
#         if attr.startswith('_'):
#             continue
#         try:
#             val = getattr(course_obj, attr)
#             val_type = type(val).__name__
#             if val_type in ("method", "builtin_function_or_method", "function"):
#                 continue
#             print(f"  {attr} ({val_type}) = {repr(val)[:120]}")
#         except Exception as e:
#             print(f"  {attr} = [ERROR: {e}]")

#     # Step 2: Check for video-related properties
#     print("\n" + "=" * 60)
#     print("LOOKING FOR VIDEO PROPERTY:")
#     print("=" * 60)
#     for attr in sorted(dir(course_obj)):
#         if 'video' in attr.lower() or 'media' in attr.lower():
#             try:
#                 val = getattr(course_obj, attr)
#                 val_type = type(val).__name__
#                 print(f"\n  Found: {attr}")
#                 print(f"  Type: {val_type}")
#                 print(f"  Value: {repr(val)[:200]}")
                
#                 # If it's a Media object, list its methods
#                 if 'Media' in val_type or 'media' in val_type:
#                     print(f"  Methods:")
#                     for m in sorted(dir(val)):
#                         if not m.startswith('_'):
#                             print(f"    - {m}")
#             except Exception as e:
#                 print(f"  {attr} = [ERROR: {e}]")


################################# TEST SCRIPT #####################################################

# test_video_stream.py
from app.integrations.palantir.foundry_service import get_course_video_content

content, content_type = get_course_video_content("1")

if content:
    print(f"✅ SUCCESS! Got {len(content)} bytes")
    print(f"   Content type: {content_type}")
    print(f"   First 4 bytes: {content[:4]}")
    with open("test_output.mp4", "wb") as f:
        f.write(content)
    print("   Saved to test_output.mp4 — play it to verify!")
else:
    print("❌ FAILED: No content returned")

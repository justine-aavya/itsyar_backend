# # test_certificate_object.py
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

# with AllowBetaFeatures():
#     client = foundry_osdk.get_client()

#     # Check what certificate-related objects exist
#     print("=" * 60)
#     print("CHECKING FOR CERTIFICATE OBJECTS:")
#     print("=" * 60)
#     for name in ["Certificate", "Certificates", "VanyarCertificate", "VanyarCertificates", "CourseCertificate"]:
#         has_it = hasattr(client.ontology.objects, name)
#         print(f"  {name}: {'✅ EXISTS' if has_it else '❌ Not found'}")

#     # Also check the Courses object for updated certificate property
#     print("\n" + "=" * 60)
#     print("COURSES — CERTIFICATE PROPERTY:")
#     print("=" * 60)
#     course_obj = client.ontology.objects.Courses.get(1)
#     cert = course_obj.certificate
#     print(f"  Type: {type(cert)}")
#     print(f"  Has .get_media_content(): {hasattr(cert, 'get_media_content')}")
#     if hasattr(cert, 'get_media_content'):
#         print("  ✅ It's now a Media property!")
#     else:
#         print(f"  Value: {repr(cert)[:300]}")

#     # List all object types that have "cert" in the name
#     print("\n" + "=" * 60)
#     print("ALL AVAILABLE OBJECT TYPES:")
#     print("=" * 60)
#     for attr in sorted(dir(client.ontology.objects)):
#         if not attr.startswith('_'):
#             print(f"  {attr}")
#################################################################################################3

# # test_content_object.py
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

# with AllowBetaFeatures():
#     client = foundry_osdk.get_client()

#     # Check Content object
#     print("=" * 60)
#     print("CONTENT OBJECTS:")
#     print("=" * 60)
#     try:
#         contents = client.ontology.objects.Content.take(20)
#         print(f"  Found: {len(contents)} items")
#         if contents:
#             c = contents[0]
#             print(f"\n  First Content attributes:")
#             for attr in sorted(dir(c)):
#                 if attr.startswith('_'):
#                     continue
#                 try:
#                     val = getattr(c, attr)
#                     val_type = type(val).__name__
#                     if val_type in ("method", "builtin_function_or_method", "function"):
#                         continue
#                     print(f"    {attr} ({val_type}) = {repr(val)[:200]}")
#                 except Exception as e:
#                     print(f"    {attr} = [ERROR: {e}]")
#     except Exception as e:
#         print(f"  ERROR: {e}")

#     # Also check VanyarProgress (useful for our progress feature)
#     print("\n" + "=" * 60)
#     print("VANYAR PROGRESS OBJECTS:")
#     print("=" * 60)
#     try:
#         progress = client.ontology.objects.VanyarProgress.take(10)
#         print(f"  Found: {len(progress)} items")
#         if progress:
#             p = progress[0]
#             print(f"\n  First Progress attributes:")
#             for attr in sorted(dir(p)):
#                 if attr.startswith('_'):
#                     continue
#                 try:
#                     val = getattr(p, attr)
#                     val_type = type(val).__name__
#                     if val_type in ("method", "builtin_function_or_method", "function"):
#                         continue
#                     print(f"    {attr} ({val_type}) = {repr(val)[:200]}")
#                 except Exception as e:
#                     print(f"    {attr} = [ERROR: {e}]")
#     except Exception as e:
#         print(f"  ERROR: {e}")

##############################################################################################################################3

# # test_curriculum_all_fields.py
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

# with AllowBetaFeatures():
#     client = foundry_osdk.get_client()
#     items = client.ontology.objects.Curriculum.take(10)

#     if items:
#         item = items[0]
#         print("ALL attributes (including None):")
#         for attr in sorted(dir(item)):
#             if attr.startswith('_'):
#                 continue
#             try:
#                 val = getattr(item, attr)
#                 val_type = type(val).__name__
#                 if val_type in ("method", "builtin_function_or_method", "function"):
#                     continue
#                 # Show EVERYTHING
#                 print(f"  {attr} = {repr(val)}")
#             except Exception as e:
#                 print(f"  {attr} = [ERROR: {e}]")
###########################################################################################################33

# test_progress_api.py
import os
from dotenv import load_dotenv
load_dotenv()

from app.integrations.palantir.foundry_service import get_course_progress

# Use a real user_id from your database
USER_ID = "8c9ec136-b92c-44f6-8425-cb0cf2848786"  # ← Change to your user ID
COURSE_ID = "1"

print(f"Testing progress for user: {USER_ID}, course: {COURSE_ID}")
print("=" * 60)

result = get_course_progress(course_id=COURSE_ID, user_id=USER_ID)

print(f"\nResult:")
for key, value in result.items():
    print(f"  {key}: {value}")

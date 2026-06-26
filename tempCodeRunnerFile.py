#             if attr.startswith('__'):
#                 continue
#             try:
#                 val = getattr(c, attr)
#                 val_type = type(val).__name__
#                 if val_type in ("method", "builtin_function_or_method", "function"):
#                     continue
#                 print(f"    {attr} ({val_type}) = {repr(val)[:250]}")
#             except Exception as e:
#                 print(f"    {attr} = [ERROR: {e}]")

#############################################################################################################3

# test_duration.py
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

with AllowBetaFeatures():
    client = foundry_osdk.get_client()

    print("COURSES — Duration Per Lesson:")
    print("=" * 60)
    courses = client.ontology.objects.Courses.take(20)
    for c in courses:
        cid = getattr(c, "course_id", "?")
        lid = getattr(c, "lesson_id", "?")
        title = getattr(c, "lesson_title", "?")
        duration = getattr(c, "duration1", "NONE")
        print(f"  course:{cid} | lesson:{lid} | {title} | duration: '{duration}'")

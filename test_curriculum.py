# test_curriculum.py
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

    print("=" * 60)
    print(f"ALL PROPERTIES ON COURSE {COURSE_ID}:")
    print("=" * 60)
    for attr in sorted(dir(course_obj)):
        if attr.startswith('_'):
            continue
        try:
            val = getattr(course_obj, attr)
            val_type = type(val).__name__
            if val_type in ("method", "builtin_function_or_method", "function"):
                continue
            if 'curricul' in attr.lower() or 'module' in attr.lower() or 'lesson' in attr.lower():
                print(f"  ⭐ {attr} ({val_type}) = {repr(val)[:300]}")
            else:
                print(f"  {attr} ({val_type}) = {repr(val)[:150]}")
        except Exception as e:
            print(f"  {attr} = [ERROR: {e}]")

    # Also check if new object types exist
    print("\n" + "=" * 60)
    print("CHECKING FOR NEW OBJECT TYPES:")
    print("=" * 60)
    for obj_type in ["VanyarTrainingModule", "VanyarExercise", "VanyarLesson", "Curriculum", "Module", "Lesson"]:
        has_it = hasattr(client.ontology.objects, obj_type)
        print(f"  {obj_type}: {'✅ EXISTS' if has_it else '❌ Not found'}")

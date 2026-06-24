# # test_new_objects.py
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

#     # Check VanyarTrainingModule
#     print("=" * 60)
#     print("VANYAR TRAINING MODULES:")
#     print("=" * 60)
#     try:
#         modules = client.ontology.objects.VanyarTrainingModule.take(50)
#         print(f"  Found: {len(modules)} modules")
#         if modules:
#             m = modules[0]
#             print(f"\n  First module attributes:")
#             for attr in sorted(dir(m)):
#                 if attr.startswith('_'):
#                     continue
#                 try:
#                     val = getattr(m, attr)
#                     val_type = type(val).__name__
#                     if val_type in ("method", "builtin_function_or_method", "function"):
#                         continue
#                     print(f"    {attr} ({val_type}) = {repr(val)[:200]}")
#                 except Exception as e:
#                     print(f"    {attr} = [ERROR: {e}]")
#     except Exception as e:
#         print(f"  ERROR: {e}")

#     # Check VanyarExercise
#     print("\n" + "=" * 60)
#     print("VANYAR EXERCISES:")
#     print("=" * 60)
#     try:
#         exercises = client.ontology.objects.VanyarExercise.take(50)
#         print(f"  Found: {len(exercises)} exercises")
#         if exercises:
#             ex = exercises[0]
#             print(f"\n  First exercise attributes:")
#             for attr in sorted(dir(ex)):
#                 if attr.startswith('_'):
#                     continue
#                 try:
#                     val = getattr(ex, attr)
#                     val_type = type(val).__name__
#                     if val_type in ("method", "builtin_function_or_method", "function"):
#                         continue
#                     print(f"    {attr} ({val_type}) = {repr(val)[:200]}")
#                 except Exception as e:
#                     print(f"    {attr} = [ERROR: {e}]")
#     except Exception as e:
#         print(f"  ERROR: {e}")
#################################################################################################################

#test_curriculum_mapping

# test_curriculum_mapping.py
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

    # 1. List all tracks
    print("=" * 60)
    print("ALL TRACKS:")
    print("=" * 60)
    tracks = client.ontology.objects.VanyarTrack.take(50)
    for t in tracks:
        print(f"  track_id: {t.track_id} | title: {getattr(t, 'title', getattr(t, 'name', '?'))}")
        # Check if tracks have course_id
        for attr in dir(t):
            if 'course' in attr.lower():
                print(f"    ⭐ {attr} = {getattr(t, attr, None)}")

    # 2. List all modules with their track_id
    print("\n" + "=" * 60)
    print("ALL MODULES (grouped by track):")
    print("=" * 60)
    modules = client.ontology.objects.VanyarTrainingModule.take(50)
    modules_sorted = sorted(modules, key=lambda m: (getattr(m, 'track_id', ''), getattr(m, 'sort_order', 0)))
    for m in modules_sorted:
        print(f"  [{m.track_id}] order:{m.sort_order} | {m.module_id} | {m.title} ({m.content_type}, {m.estimated_minutes}min)")

    # 3. List all exercises with their module_id
    print("\n" + "=" * 60)
    print("ALL EXERCISES (grouped by module):")
    print("=" * 60)
    exercises = client.ontology.objects.VanyarExercise.take(50)
    exercises_sorted = sorted(exercises, key=lambda e: (getattr(e, 'module_id', ''), getattr(e, 'sort_order', 0) or 0))
    for ex in exercises_sorted:
        print(f"  [{ex.module_id}] | {ex.exercise_id} | {ex.title} ({ex.type}, max:{ex.max_score})")

    # 4. Check if courses have a track_id field
    print("\n" + "=" * 60)
    print("COURSES — CHECKING FOR TRACK LINK:")
    print("=" * 60)
    courses = client.ontology.objects.Courses.take(10)
    for c in courses:
        print(f"  course_id: {c.course_id} | {c.course_name1}")
        for attr in sorted(dir(c)):
            if 'track' in attr.lower() or 'module' in attr.lower():
                print(f"    ⭐ {attr} = {getattr(c, attr, None)}")

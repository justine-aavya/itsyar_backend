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

# #test_curriculum_mapping

# # test_curriculum_mapping.py
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

#     # 1. List all tracks
#     print("=" * 60)
#     print("ALL TRACKS:")
#     print("=" * 60)
#     tracks = client.ontology.objects.VanyarTrack.take(50)
#     for t in tracks:
#         print(f"  track_id: {t.track_id} | title: {getattr(t, 'title', getattr(t, 'name', '?'))}")
#         # Check if tracks have course_id
#         for attr in dir(t):
#             if 'course' in attr.lower():
#                 print(f"    ⭐ {attr} = {getattr(t, attr, None)}")

#     # 2. List all modules with their track_id
#     print("\n" + "=" * 60)
#     print("ALL MODULES (grouped by track):")
#     print("=" * 60)
#     modules = client.ontology.objects.VanyarTrainingModule.take(50)
#     modules_sorted = sorted(modules, key=lambda m: (getattr(m, 'track_id', ''), getattr(m, 'sort_order', 0)))
#     for m in modules_sorted:
#         print(f"  [{m.track_id}] order:{m.sort_order} | {m.module_id} | {m.title} ({m.content_type}, {m.estimated_minutes}min)")

#     # 3. List all exercises with their module_id
#     print("\n" + "=" * 60)
#     print("ALL EXERCISES (grouped by module):")
#     print("=" * 60)
#     exercises = client.ontology.objects.VanyarExercise.take(50)
#     exercises_sorted = sorted(exercises, key=lambda e: (getattr(e, 'module_id', ''), getattr(e, 'sort_order', 0) or 0))
#     for ex in exercises_sorted:
#         print(f"  [{ex.module_id}] | {ex.exercise_id} | {ex.title} ({ex.type}, max:{ex.max_score})")

#     # 4. Check if courses have a track_id field
#     print("\n" + "=" * 60)
#     print("COURSES — CHECKING FOR TRACK LINK:")
#     print("=" * 60)
#     courses = client.ontology.objects.Courses.take(10)
#     for c in courses:
#         print(f"  course_id: {c.course_id} | {c.course_name1}")
#         for attr in sorted(dir(c)):
#             if 'track' in attr.lower() or 'module' in attr.lower():
#                 print(f"    ⭐ {attr} = {getattr(c, attr, None)}")

#########################################################################################################################################

# # test_progress.py
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

#     # Check VanyarProgress
#     print("=" * 60)
#     print("VANYAR PROGRESS — ALL RECORDS:")
#     print("=" * 60)
#     try:
#         items = client.ontology.objects.VanyarProgress.take(50)
#         print(f"  Found: {len(items)} items\n")

#         for item in items:
#             print(f"  progress_id: {item.progress_id}")
#             print(f"    user_id: {item.user_id}")
#             print(f"    module_id: {item.module_id}")
#             print(f"    status: {item.status}")
#             print(f"    score: {item.score}")
#             print(f"    completed_at: {item.completed_at}")
#             print()

#     except Exception as e:
#         print(f"  ERROR: {e}")

#     # Also check VanyarEnrolment for completion fields
#     print("=" * 60)
#     print("VANYAR ENROLMENT — CHECKING FOR COMPLETION FIELDS:")
#     print("=" * 60)
#     try:
#         enrollments = client.ontology.objects.VanyarEnrolment.take(10)
#         if enrollments:
#             e = enrollments[0]
#             print(f"  First enrollment attributes:")
#             for attr in sorted(dir(e)):
#                 if attr.startswith('_'):
#                     continue
#                 try:
#                     val = getattr(e, attr)
#                     val_type = type(val).__name__
#                     if val_type in ("method", "builtin_function_or_method", "function"):
#                         continue
#                     if 'progress' in attr.lower() or 'complet' in attr.lower() or 'percent' in attr.lower() or 'status' in attr.lower():
#                         print(f"    ⭐ {attr} ({val_type}) = {repr(val)[:150]}")
#                     else:
#                         print(f"    {attr} ({val_type}) = {repr(val)[:150]}")
#                 except:
#                     pass
#     except Exception as e:
#         print(f"  ERROR: {e}")
#############################################################################################################################################################

# # test_debug_curriculum.py
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

# COURSE_ID = "1"

# with AllowBetaFeatures():
#     client = foundry_osdk.get_client()
    
#     print("Fetching ALL Curriculum objects...")
#     all_items = client.ontology.objects.Curriculum.take(100)
#     print(f"Total found: {len(all_items)}")
    
#     for item in all_items:
#         cid = getattr(item, "course_id", "NONE")
#         title = getattr(item, "title1", "NONE")
#         print(f"  course_id: '{cid}' (type: {type(cid).__name__}) | title: {title}")
        
#         # Check if it matches
#         matches = str(cid) == str(COURSE_ID)
#         print(f"    str('{cid}') == str('{COURSE_ID}') → {matches}")
#######################################################################################################################################################

# # test_hackathon_objects.py
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

#     # ═══ HACKATHONS ═══
#     print("=" * 60)
#     print("HACKATHONS OBJECT:")
#     print("=" * 60)
#     try:
#         items = client.ontology.objects.Hackathons.take(10)
#         print(f"  Found: {len(items)} items")
#         if items:
#             print(f"\n  First item attributes:")
#             for attr in sorted(dir(items[0])):
#                 if attr.startswith('_'):
#                     continue
#                 try:
#                     val = getattr(items[0], attr)
#                     val_type = type(val).__name__
#                     if val_type in ("method", "builtin_function_or_method", "function"):
#                         continue
#                     print(f"    {attr} ({val_type}) = {repr(val)[:200]}")
#                 except Exception as e:
#                     print(f"    {attr} = [ERROR: {e}]")
#     except Exception as e:
#         print(f"  ERROR: {e}")

#     # ═══ VANYAR TEAM ═══
#     print("\n" + "=" * 60)
#     print("VANYAR TEAM OBJECT:")
#     print("=" * 60)
#     try:
#         teams = client.ontology.objects.VanyarTeam.take(10)
#         print(f"  Found: {len(teams)} items")
#         if teams:
#             print(f"\n  First team attributes:")
#             for attr in sorted(dir(teams[0])):
#                 if attr.startswith('_'):
#                     continue
#                 try:
#                     val = getattr(teams[0], attr)
#                     val_type = type(val).__name__
#                     if val_type in ("method", "builtin_function_or_method", "function"):
#                         continue
#                     print(f"    {attr} ({val_type}) = {repr(val)[:200]}")
#                 except Exception as e:
#                     print(f"    {attr} = [ERROR: {e}]")

#             # Print all teams summary
#             print(f"\n  All {len(teams)} teams:")
#             for t in teams:
#                 name = getattr(t, 'name', getattr(t, 'team_name', '?'))
#                 tid = getattr(t, 'team_id', getattr(t, 'id', '?'))
#                 print(f"    id:{tid} | name:{name}")
#     except Exception as e:
#         print(f"  ERROR: {e}")

#     # ═══ CHECK ACTIONS ═══
#     print("\n" + "=" * 60)
#     print("AVAILABLE ACTIONS (hackathon-related):")
#     print("=" * 60)
#     for attr in sorted(dir(client.ontology.actions)):
#         if not attr.startswith('_'):
#             if 'hack' in attr.lower() or 'team' in attr.lower() or 'register' in attr.lower() or 'join' in attr.lower():
#                 print(f"  ⭐ {attr}")
#             else:
#                 print(f"  {attr}")
############################################################################################################################################

# # test_events_as_hackathons.py
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

#     print("=" * 60)
#     print("ALL VANYAR EVENTS:")
#     print("=" * 60)
#     events = client.ontology.objects.VanyarEvent.take(20)
#     print(f"  Found: {len(events)} events\n")

#     if events:
#         # Show first event's full attributes
#         print("  First event ALL attributes:")
#         e = events[0]
#         for attr in sorted(dir(e)):
#             if attr.startswith('_'):
#                 continue
#             try:
#                 val = getattr(e, attr)
#                 val_type = type(val).__name__
#                 if val_type in ("method", "builtin_function_or_method", "function"):
#                     continue
#                 print(f"    {attr} ({val_type}) = {repr(val)[:200]}")
#             except:
#                 pass

#         # Summary of all events
#         print(f"\n  All {len(events)} events summary:")
#         for e in events:
#             eid = getattr(e, 'event_id', '?')
#             title = getattr(e, 'title', getattr(e, 'name', '?'))
#             status = getattr(e, 'status', '?')
#             etype = getattr(e, 'event_type', getattr(e, 'type', '?'))
#             start = getattr(e, 'start_date', getattr(e, 'startDate', '?'))
#             end = getattr(e, 'end_date', getattr(e, 'endDate', '?'))
#             print(f"    [{eid}] {title} | status:{status} | type:{etype} | {start} → {end}")

#     # Check which teams belong to which events
#     print("\n" + "=" * 60)
#     print("TEAMS → EVENTS MAPPING:")
#     print("=" * 60)
#     teams = client.ontology.objects.VanyarTeam.take(10)
#     for t in teams:
#         tid = getattr(t, 'team_id', '?')
#         name = getattr(t, 'name', '?')
#         eid = getattr(t, 'event_id', '?')
#         captain = getattr(t, 'captain_user_id', '?')
#         print(f"  Team: {name} ({tid}) → event: {eid} | captain: {captain}")
#######################################################################################################33

# test_get_course.py
from app.integrations.palantir.foundry_service import get_single_course

result = get_single_course("1")
print(f"Result: {result}")
print(f"Type: {type(result)}")

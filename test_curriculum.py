# # test_curriculum.py
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

#     print("=" * 60)
#     print(f"ALL PROPERTIES ON COURSE {COURSE_ID}:")
#     print("=" * 60)
#     for attr in sorted(dir(course_obj)):
#         if attr.startswith('_'):
#             continue
#         try:
#             val = getattr(course_obj, attr)
#             val_type = type(val).__name__
#             if val_type in ("method", "builtin_function_or_method", "function"):
#                 continue
#             if 'curricul' in attr.lower() or 'module' in attr.lower() or 'lesson' in attr.lower():
#                 print(f"  ⭐ {attr} ({val_type}) = {repr(val)[:300]}")
#             else:
#                 print(f"  {attr} ({val_type}) = {repr(val)[:150]}")
#         except Exception as e:
#             print(f"  {attr} = [ERROR: {e}]")

#     # Also check if new object types exist
#     print("\n" + "=" * 60)
#     print("CHECKING FOR NEW OBJECT TYPES:")
#     print("=" * 60)
#     for obj_type in ["VanyarTrainingModule", "VanyarExercise", "VanyarLesson", "Curriculum", "Module", "Lesson"]:
#         has_it = hasattr(client.ontology.objects, obj_type)
#         print(f"  {obj_type}: {'✅ EXISTS' if has_it else '❌ Not found'}")
##############################################################################################################################3

# # test_curriculum_new.py
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

#     # Check ALL available object types
#     print("=" * 60)
#     print("ALL OBJECT TYPES IN SDK 0.22:")
#     print("=" * 60)
#     for attr in sorted(dir(client.ontology.objects)):
#         if not attr.startswith('_'):
#             print(f"  {attr}")

#     # Check if Courses now has track_id
#     print("\n" + "=" * 60)
#     print("COURSES — CHECKING FOR track_id OR NEW PROPERTIES:")
#     print("=" * 60)
#     course_obj = client.ontology.objects.Courses.get(1)
#     for attr in sorted(dir(course_obj)):
#         if attr.startswith('_'):
#             continue
#         try:
#             val = getattr(course_obj, attr)
#             val_type = type(val).__name__
#             if val_type in ("method", "builtin_function_or_method", "function"):
#                 continue
#             print(f"  {attr} ({val_type}) = {repr(val)[:150]}")
#         except Exception as e:
#             print(f"  {attr} = [ERROR: {e}]")
########################################################################################################

# # test_curriculum_obj.py
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

#     # Explore Curriculum object
#     print("=" * 60)
#     print("CURRICULUM OBJECTS:")
#     print("=" * 60)
#     try:
#         items = client.ontology.objects.Curriculum.take(20)
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

#             # Print ALL items (summary)
#             print(f"\n  All {len(items)} items:")
#             for item in items:
#                 course_id = getattr(item, 'course_id', None)
#                 title = getattr(item, 'title', getattr(item, 'name', '?'))
#                 module_id = getattr(item, 'module_id', None)
#                 sort = getattr(item, 'sort_order', getattr(item, 'order', None))
#                 print(f"    course:{course_id} | module:{module_id} | order:{sort} | {title}")
#     except Exception as e:
#         print(f"  ERROR: {e}")

#######################################################################################################################3

# # test_vanyar_team_v26.py
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
#     print("VANYAR TEAM — ALL PROPERTIES (SDK 0.26):")
#     print("=" * 60)
#     teams = client.ontology.objects.VanyarTeam.take(10)
#     print(f"  Found: {len(teams)} teams")

#     if teams:
#         t = teams[0]
#         print(f"\n  First team — ALL attributes:")
#         for attr in sorted(dir(t)):
#             if attr.startswith('__'):
#                 continue
#             try:
#                 val = getattr(t, attr)
#                 val_type = type(val).__name__
#                 if val_type in ("method", "builtin_function_or_method", "function"):
#                     continue
#                 print(f"    {attr} ({val_type}) = {repr(val)[:200]}")
#             except Exception as e:
#                 print(f"    {attr} = [ERROR: {e}]")

#         # All teams summary
#         print(f"\n  All {len(teams)} teams:")
#         for t in teams:
#             tid = getattr(t, 'team_id', '?')
#             name = getattr(t, 'name', '?')
#             captain = getattr(t, 'captain_user_id', '?')
#             eid = getattr(t, 'event_id', '?')
#             members = getattr(t, 'members', getattr(t, 'member_ids', getattr(t, 'member_count', '?')))
#             print(f"    [{tid}] {name} | captain:{captain} | event:{eid} | members:{members}")
#####################################################################################################################

# # test_team_members.py
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
#     teams = client.ontology.objects.VanyarTeam.take(5)

#     if teams:
#         team = teams[0]
#         print(f"Team: {team.name} ({team.team_id})")
#         print(f"Captain: {team.captain_user_id}")
#         print(f"\nCalling team.members()...")

#         try:
#             members = team.members()
#             print(f"Type: {type(members)}")
#             print(f"Members: {members}")

#             # Try .take() if it's a query
#             if hasattr(members, 'take'):
#                 member_list = members.take(20)
#                 print(f"\nFound {len(member_list)} members:")
#                 for m in member_list:
#                     print(f"  {dir(m)[:10]}")
#                     for attr in sorted(dir(m)):
#                         if attr.startswith('_'):
#                             continue
#                         try:
#                             val = getattr(m, attr)
#                             val_type = type(val).__name__
#                             if val_type in ("method", "builtin_function_or_method", "function"):
#                                 continue
#                             print(f"    {attr} ({val_type}) = {repr(val)[:150]}")
#                         except:
#                             pass
#                     print()
#         except Exception as e:
#             print(f"Error: {e}")

#########################################################################################################################

# # test_hackathon_v26.py
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
#     items = client.ontology.objects.Hackathons.take(10)
#     print(f"Found: {len(items)} hackathons\n")

#     if items:
#         h = items[0]
#         print("ALL attributes:")
#         for attr in sorted(dir(h)):
#             if attr.startswith('__'):
#                 continue
#             try:
#                 val = getattr(h, attr)
#                 val_type = type(val).__name__
#                 if val_type in ("method", "builtin_function_or_method", "function"):
#                     continue
#                 print(f"  {attr} ({val_type}) = {repr(val)[:300]}")
#             except Exception as e:
#                 print(f"  {attr} = [ERROR: {e}]")
##########################################################################################################33

# # test_courses_lessons.py
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
#     print("ALL COURSES (checking lessonId/lessonTitle):")
#     print("=" * 60)
#     courses = client.ontology.objects.Courses.take(20)
#     print(f"  Found: {len(courses)} items\n")

#     for c in courses:
#         cid = getattr(c, "course_id", "?")
#         title = getattr(c, "course_name1", getattr(c, "title", "?"))
#         lid = getattr(c, "lessonId", getattr(c, "lesson_id", "?"))
#         ltitle = getattr(c, "lessonTitle", getattr(c, "lesson_title", "?"))
#         print(f"  course_id:{cid} | lessonId:{lid} | lessonTitle:{ltitle} | course:{title}")

#     # Show ALL properties on first item
#     if courses:
#         print(f"\n{'=' * 60}")
#         print("FIRST COURSE — ALL ATTRIBUTES:")
#         print("=" * 60)
#         c = courses[0]
#         for attr in sorted(dir(c)):
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

# # test_duration.py
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

#     print("COURSES — Duration Per Lesson:")
#     print("=" * 60)
#     courses = client.ontology.objects.Courses.take(20)
#     for c in courses:
#         cid = getattr(c, "course_id", "?")
#         lid = getattr(c, "lesson_id", "?")
#         title = getattr(c, "lesson_title", "?")
#         duration = getattr(c, "duration1", "NONE")
#         print(f"  course:{cid} | lesson:{lid} | {title} | duration: '{duration}'")

###########################################################################################3

# # test_all_course_objects.py
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

#     # List ALL available object types
#     print("=" * 60)
#     print("ALL AVAILABLE OBJECT TYPES:")
#     print("=" * 60)
#     for attr in sorted(dir(client.ontology.objects)):
#         if not attr.startswith('_'):
#             print(f"  {attr}")

#     # Courses
#     print("\n" + "=" * 60)
#     print("COURSES — All Properties:")
#     print("=" * 60)
#     courses = client.ontology.objects.Courses.take(5)
#     if courses:
#         c = courses[0]
#         for attr in sorted(dir(c)):
#             if attr.startswith('__'):
#                 continue
#             try:
#                 val = getattr(c, attr)
#                 val_type = type(val).__name__
#                 if val_type in ("method", "builtin_function_or_method", "function"):
#                     continue
#                 print(f"    {attr} ({val_type}) = {repr(val)[:200]}")
#             except Exception as e:
#                 print(f"    {attr} = [ERROR: {e}]")

#     # Quizes
#     print("\n" + "=" * 60)
#     print("QUIZES — All Properties:")
#     print("=" * 60)
#     quizzes = client.ontology.objects.Quizes.take(5)
#     if quizzes:
#         q = quizzes[0]
#         for attr in sorted(dir(q)):
#             if attr.startswith('__'):
#                 continue
#             try:
#                 val = getattr(q, attr)
#                 val_type = type(val).__name__
#                 if val_type in ("method", "builtin_function_or_method", "function"):
#                     continue
#                 print(f"    {attr} ({val_type}) = {repr(val)[:200]}")
#             except Exception as e:
#                 print(f"    {attr} = [ERROR: {e}]")

#     # VanyarEnrolment
#     print("\n" + "=" * 60)
#     print("VANYAR ENROLMENT — All Properties:")
#     print("=" * 60)
#     enrollments = client.ontology.objects.VanyarEnrolment.take(5)
#     if enrollments:
#         e = enrollments[0]
#         for attr in sorted(dir(e)):
#             if attr.startswith('__'):
#                 continue
#             try:
#                 val = getattr(e, attr)
#                 val_type = type(val).__name__
#                 if val_type in ("method", "builtin_function_or_method", "function"):
#                     continue
#                 print(f"    {attr} ({val_type}) = {repr(val)[:200]}")
#             except Exception as e2:
#                 print(f"    {attr} = [ERROR: {e2}]")

#     # VanyarProgress
#     print("\n" + "=" * 60)
#     print("VANYAR PROGRESS — All Properties:")
#     print("=" * 60)
#     progress = client.ontology.objects.VanyarProgress.take(5)
#     if progress:
#         p = progress[0]
#         for attr in sorted(dir(p)):
#             if attr.startswith('__'):
#                 continue
#             try:
#                 val = getattr(p, attr)
#                 val_type = type(val).__name__
#                 if val_type in ("method", "builtin_function_or_method", "function"):
#                     continue
#                 print(f"    {attr} ({val_type}) = {repr(val)[:200]}")
#             except Exception as e:
#                 print(f"    {attr} = [ERROR: {e}]")

#     # Actions
#     print("\n" + "=" * 60)
#     print("ALL ACTIONS:")
#     print("=" * 60)
#     for attr in sorted(dir(client.ontology.actions)):
#         if not attr.startswith('_'):
#             print(f"  {attr}")
##############################################################################3

# # test_sdk_v27.py
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

#     # All object types
#     print("=" * 60)
#     print("ALL OBJECT TYPES (SDK 0.27):")
#     print("=" * 60)
#     for attr in sorted(dir(client.ontology.objects)):
#         if not attr.startswith('_'):
#             print(f"  {attr}")

#     # All actions
#     print("\n" + "=" * 60)
#     print("ALL ACTIONS (SDK 0.27):")
#     print("=" * 60)
#     for attr in sorted(dir(client.ontology.actions)):
#         if not attr.startswith('_'):
#             print(f"  {attr}")

#     # Courses — check for new properties
#     print("\n" + "=" * 60)
#     print("COURSES — All Properties:")
#     print("=" * 60)
#     courses = client.ontology.objects.Courses.take(2)
#     if courses:
#         c = courses[0]
#         for attr in sorted(dir(c)):
#             if attr.startswith('__'):
#                 continue
#             try:
#                 val = getattr(c, attr)
#                 val_type = type(val).__name__
#                 if val_type in ("method", "builtin_function_or_method", "function"):
#                     continue
#                 print(f"    {attr} ({val_type}) = {repr(val)[:200]}")
#             except Exception as e:
#                 print(f"    {attr} = [ERROR: {e}]")

#     # Hackathons — check for new properties
#     print("\n" + "=" * 60)
#     print("HACKATHONS — All Properties:")
#     print("=" * 60)
#     hacks = client.ontology.objects.Hackathons.take(2)
#     if hacks:
#         h = hacks[0]
#         for attr in sorted(dir(h)):
#             if attr.startswith('__'):
#                 continue
#             try:
#                 val = getattr(h, attr)
#                 val_type = type(val).__name__
#                 if val_type in ("method", "builtin_function_or_method", "function"):
#                     continue
#                 print(f"    {attr} ({val_type}) = {repr(val)[:200]}")
#             except Exception as e:
#                 print(f"    {attr} = [ERROR: {e}]")

###############################################################################################################333


# # test_module_summaries.py
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
#     courses = client.ontology.objects.Courses.take(20)

#     print("CHECKING MODULE-SPECIFIC SUMMARIES:")
#     print("=" * 60)
#     for c in courses:
#         cid = getattr(c, "course_id", "?")
#         lid = getattr(c, "lesson_id", "?")
#         title = getattr(c, "lesson_title", "?")
#         desc = getattr(c, "description", None)
#         about = getattr(c, "about_the_course", None)
#         print(f"\n  course:{cid} | lesson:{lid} | {title}")
#         print(f"    description: {repr(desc)[:150] if desc else 'None'}")
#         print(f"    about_the_course: {repr(about)[:150] if about else 'None'}")

###################################################################################################3


# # test_module_summary_field.py
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
#     courses = client.ontology.objects.Courses.take(10)

#     print("CHECKING FOR 'SUMMARY' PROPERTY:")
#     print("=" * 60)
#     for c in courses:
#         cid = getattr(c, "course_id", "?")
#         lid = getattr(c, "lesson_id", "?")
#         title = getattr(c, "lesson_title", "?")
        
#         # Check for summary-related fields
#         summary = getattr(c, "summary", None)
#         summary1 = getattr(c, "summary1", None)
#         lesson_summary = getattr(c, "lesson_summary", None)
        
#         print(f"\n  course:{cid} | lesson:{lid} | {title}")
#         print(f"    summary: {repr(summary)[:200] if summary else 'None'}")
#         print(f"    summary1: {repr(summary1)[:200] if summary1 else 'None'}")
#         print(f"    lesson_summary: {repr(lesson_summary)[:200] if lesson_summary else 'None'}")
        
#         # Also check ALL attributes for anything with "summ" in the name
#         for attr in sorted(dir(c)):
#             if 'summ' in attr.lower() and not attr.startswith('_'):
#                 val = getattr(c, attr, None)
#                 if val:
#                     print(f"    ⭐ {attr}: {repr(val)[:200]}")

############################################################################################################3

# # test_progress_details.py
# import os, inspect
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

#     # Check ProgressDetails object
#     print("=" * 60)
#     print("PROGRESS DETAILS OBJECT:")
#     print("=" * 60)
#     try:
#         items = client.ontology.objects.ProgressDetails.take(10)
#         print(f"  Found: {len(items)} items")
#         if items:
#             p = items[0]
#             for attr in sorted(dir(p)):
#                 if attr.startswith('__'):
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

#     # Check create_progress_details action signature
#     print("\n" + "=" * 60)
#     print("CREATE_PROGRESS_DETAILS ACTION:")
#     print("=" * 60)
#     try:
#         sig = inspect.signature(client.ontology.actions.create_progress_details)
#         params = list(sig.parameters.keys())
#         print(f"  Parameters: {params}")
#     except Exception as e:
#         print(f"  ERROR: {e}")

#     # Check complete_module action signature
#     print("\n" + "=" * 60)
#     print("COMPLETE_MODULE ACTION:")
#     print("=" * 60)
#     try:
#         sig = inspect.signature(client.ontology.actions.complete_module)
#         params = list(sig.parameters.keys())
#         print(f"  Parameters: {params}")
#     except Exception as e:
#         print(f"  ERROR: {e}")

##################################################################################################################

# # test_find_progress_objects.py
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

#     print("ALL OBJECTS WITH 'PROGRESS' IN NAME:")
#     for attr in sorted(dir(client.ontology.objects)):
#         if not attr.startswith('_'):
#             if 'progress' in attr.lower() or 'detail' in attr.lower():
#                 print(f"  ⭐ {attr}")
#             else:
#                 print(f"  {attr}")

#     print("\nALL ACTIONS WITH 'PROGRESS' IN NAME:")
#     for attr in sorted(dir(client.ontology.actions)):
#         if not attr.startswith('_'):
#             if 'progress' in attr.lower() or 'detail' in attr.lower() or 'complete' in attr.lower():
#                 print(f"  ⭐ {attr}")
################################################################################################################3

# # test_progress_details_v28.py
# import os, inspect
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

#     # ProgressDetails object
#     print("=" * 60)
#     print("PROGRESS DETAILS — All Properties:")
#     print("=" * 60)
#     try:
#         items = client.ontology.objects.ProgressDetails.take(10)
#         print(f"  Found: {len(items)} items")
#         if items:
#             p = items[0]
#             for attr in sorted(dir(p)):
#                 if attr.startswith('__'):
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

#     # create_progress_details action
#     print("\n" + "=" * 60)
#     print("CREATE_PROGRESS_DETAILS ACTION:")
#     print("=" * 60)
#     try:
#         sig = inspect.signature(client.ontology.actions.create_progress_details)
#         print(f"  Parameters: {list(sig.parameters.keys())}")
#     except Exception as e:
#         print(f"  ERROR: {e}")

#     # modify_progress_deatils action
#     print("\n" + "=" * 60)
#     print("MODIFY_PROGRESS_DEATILS ACTION:")
#     print("=" * 60)
#     try:
#         sig = inspect.signature(client.ontology.actions.modify_progress_deatils)
#         print(f"  Parameters: {list(sig.parameters.keys())}")
#     except Exception as e:
#         print(f"  ERROR: {e}")

#     # complete_module action
#     print("\n" + "=" * 60)
#     print("COMPLETE_MODULE ACTION:")
#     print("=" * 60)
#     try:
#         sig = inspect.signature(client.ontology.actions.complete_module)
#         print(f"  Parameters: {list(sig.parameters.keys())}")
#     except Exception as e:
#         print(f"  ERROR: {e}")

#     # VanyarProgress (overall)
#     print("\n" + "=" * 60)
#     print("VANYAR PROGRESS — All Properties:")
#     print("=" * 60)
#     try:
#         items = client.ontology.objects.VanyarProgress.take(5)
#         print(f"  Found: {len(items)} items")
#         if items:
#             p = items[0]
#             for attr in sorted(dir(p)):
#                 if attr.startswith('__'):
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

##########################################################################

# test_presigned_video.py
import os, inspect
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
    courses = client.ontology.objects.Courses.take(5)
    
    # Get first course with lesson_id = 1
    course = next((c for c in courses if getattr(c, "lesson_id", 0) == 1), courses[0])

    print("=" * 60)
    print("VIDEO MEDIA OBJECT — All Methods:")
    print("=" * 60)
    video = course.video
    for attr in sorted(dir(video)):
        if not attr.startswith('_'):
            print(f"  {attr}")

    print("\n" + "=" * 60)
    print("GET_MEDIA_REFERENCE() Result:")
    print("=" * 60)
    try:
        ref = video.get_media_reference()
        print(f"  Type: {type(ref)}")
        print(f"  Value: {repr(ref)[:500]}")
        # Check if it has URL or RID
        if hasattr(ref, '__dict__'):
            print(f"  Dict: {ref.__dict__}")
        if isinstance(ref, dict):
            for k, v in ref.items():
                print(f"    {k}: {v}")
    except Exception as e:
        print(f"  ERROR: {e}")

    print("\n" + "=" * 60)
    print("GET_MEDIA_METADATA() Result:")
    print("=" * 60)
    try:
        meta = video.get_media_metadata()
        print(f"  Type: {type(meta)}")
        print(f"  Value: {repr(meta)[:500]}")
        if hasattr(meta, '__dict__'):
            print(f"  Dict: {meta.__dict__}")
    except Exception as e:
        print(f"  ERROR: {e}")

    print("\n" + "=" * 60)
    print("GET_MEDIA_FULL_METADATA() Result:")
    print("=" * 60)
    try:
        full_meta = video.get_media_full_metadata()
        print(f"  Type: {type(full_meta)}")
        print(f"  Value: {repr(full_meta)[:500]}")
        if hasattr(full_meta, '__dict__'):
            print(f"  Dict: {full_meta.__dict__}")
    except Exception as e:
        print(f"  ERROR: {e}")

    # Check if we can construct a direct URL using the OAuth token
    print("\n" + "=" * 60)
    print("TRYING DIRECT MEDIA URL WITH TOKEN:")
    print("=" * 60)
    import requests
    foundry_url = os.getenv("FOUNDRY_URL", "").rstrip("/")
    ontology_rid = os.getenv("FOUNDRY_ONTOLOGY_RID", "")
    
    # Get fresh token
    token_resp = requests.post(f"{foundry_url}/multipass/api/oauth2/token", data={
        "grant_type": "client_credentials",
        "client_id": os.getenv("FOUNDRY_CLIENT_ID"),
        "client_secret": os.getenv("FOUNDRY_CLIENT_SECRET"),
    }, timeout=10)
    token = token_resp.json().get("access_token")
    
    # Try direct media URL with token as query param
    test_urls = [
        f"{foundry_url}/api/v2/ontologies/{ontology_rid}/objects/Courses/1/media/video/content?access_token={token}",
        f"{foundry_url}/api/v2/ontologies/{ontology_rid}/objects/Courses/1/media/video/content?token={token}",
        f"{foundry_url}/api/v2/ontologies/{ontology_rid}/objects/Courses/1/media/video/content?authorization={token}",
    ]
    
    for url in test_urls:
        resp = requests.get(url, timeout=10, stream=True)
        ct = resp.headers.get("content-type", "")
        print(f"  [{resp.status_code}] {ct[:30]} → ...?{url.split('?')[1][:20]}...")
        if resp.status_code == 200 and "video" in ct:
            print(f"    ✅ WORKS! Direct URL with token in query param!")
            break

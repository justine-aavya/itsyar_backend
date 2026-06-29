# # test_hackathons_v25.py
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
#     print("HACKATHONS OBJECT (SDK 0.25):")
#     print("=" * 60)
#     try:
#         items = client.ontology.objects.Hackathons.take(20)
#         print(f"  Found: {len(items)} items")

#         if items:
#             print(f"\n  First item — ALL attributes:")
#             for attr in sorted(dir(items[0])):
#                 if attr.startswith('_'):
#                     continue
#                 try:
#                     val = getattr(items[0], attr)
#                     val_type = type(val).__name__
#                     if val_type in ("method", "builtin_function_or_method", "function"):
#                         continue
#                     print(f"    {attr} ({val_type}) = {repr(val)[:250]}")
#                 except Exception as e:
#                     print(f"    {attr} = [ERROR: {e}]")

#             # Summary of all hackathons
#             print(f"\n  All {len(items)} hackathons:")
#             for h in items:
#                 hid = getattr(h, 'hackathon_id', getattr(h, 'course_id', getattr(h, 'id', '?')))
#                 title = getattr(h, 'title1', getattr(h, 'title', getattr(h, 'name', '?')))
#                 status = getattr(h, 'status1', getattr(h, 'status', '?'))
#                 start = getattr(h, 'startDate', getattr(h, 'start_date', '?'))
#                 end = getattr(h, 'endDate', getattr(h, 'end_date', '?'))
#                 print(f"    [{hid}] {title} | status:{status} | {start} → {end}")
#     except Exception as e:
#         print(f"  ERROR: {e}")

#################################################################################################################

# # test_hackathon_all_props.py
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
#     items = client.ontology.objects.Hackathons.take(5)

#     if items:
#         h = items[0]
#         print("ALL attributes (including BETA and hidden):")
#         print("=" * 60)
#         for attr in sorted(dir(h)):
#             if attr.startswith('__'):
#                 continue
#             try:
#                 val = getattr(h, attr)
#                 val_type = type(val).__name__
#                 if val_type in ("method", "builtin_function_or_method", "function"):
#                     continue
#                 print(f"  {attr} ({val_type}) = {repr(val)[:250]}")
#             except Exception as e:
#                 print(f"  {attr} = [BETA/ERROR: {e}]")
#############################################################################################################
# # test_team_object.py
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

#     # Check for Team objects
#     print("=" * 60)
#     print("CHECKING TEAM-RELATED OBJECTS:")
#     print("=" * 60)
#     for name in ["Team", "Teams", "VanyarTeam", "HackathonTeam"]:
#         has_it = hasattr(client.ontology.objects, name)
#         print(f"  {name}: {'✅ EXISTS' if has_it else '❌ Not found'}")

#     # Explore VanyarTeam (known)
#     print("\n" + "=" * 60)
#     print("VANYAR TEAM — ALL PROPERTIES:")
#     print("=" * 60)
#     teams = client.ontology.objects.VanyarTeam.take(10)
#     print(f"  Found: {len(teams)} teams")
#     if teams:
#         t = teams[0]
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

#     # Check if "Team" exists separately
#     if hasattr(client.ontology.objects, "Team"):
#         print("\n" + "=" * 60)
#         print("TEAM OBJECT (separate from VanyarTeam):")
#         print("=" * 60)
#         team_items = client.ontology.objects.Team.take(10)
#         print(f"  Found: {len(team_items)} items")
#         if team_items:
#             for attr in sorted(dir(team_items[0])):
#                 if attr.startswith('__'):
#                     continue
#                 try:
#                     val = getattr(team_items[0], attr)
#                     val_type = type(val).__name__
#                     if val_type in ("method", "builtin_function_or_method", "function"):
#                         continue
#                     print(f"    {attr} ({val_type}) = {repr(val)[:200]}")
#                 except Exception as e:
#                     print(f"    {attr} = [ERROR: {e}]")
##########################################################################################################33333

# # test_timeline_prizes.py
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

#     # Timeline
#     print("=" * 60)
#     print("TIMELINE OBJECT:")
#     print("=" * 60)
#     try:
#         items = client.ontology.objects.Timeline.take(10)
#         print(f"  Found: {len(items)} items")
#         if items:
#             for item in items:
#                 print(f"\n  Record:")
#                 for attr in sorted(dir(item)):
#                     if attr.startswith('__'):
#                         continue
#                     try:
#                         val = getattr(item, attr)
#                         val_type = type(val).__name__
#                         if val_type in ("method", "builtin_function_or_method", "function"):
#                             continue
#                         if not attr.startswith('_'):
#                             print(f"    {attr} ({val_type}) = {repr(val)[:200]}")
#                     except:
#                         pass
#     except Exception as e:
#         print(f"  ERROR: {e}")

#     # WinningPrize
#     print("\n" + "=" * 60)
#     print("WINNING PRIZE OBJECT:")
#     print("=" * 60)
#     try:
#         items = client.ontology.objects.WinningPrize.take(10)
#         print(f"  Found: {len(items)} items")
#         if items:
#             for item in items:
#                 print(f"\n  Record:")
#                 for attr in sorted(dir(item)):
#                     if attr.startswith('__'):
#                         continue
#                     try:
#                         val = getattr(item, attr)
#                         val_type = type(val).__name__
#                         if val_type in ("method", "builtin_function_or_method", "function"):
#                             continue
#                         if not attr.startswith('_'):
#                             print(f"    {attr} ({val_type}) = {repr(val)[:200]}")
#                     except:
#                         pass
#     except Exception as e:
#         print(f"  ERROR: {e}")
########################################################################################3
# # test_take_timeline.py
# from app.integrations.palantir.foundry_service import _take_objects

# items = _take_objects("Timeline", 100)
# print(f"Found: {len(items)} items")
# for t in items:
#     print(f"  {getattr(t, 'hackathon_id1', '?')} | {getattr(t, 'label1', '?')} | {getattr(t, 'date1', '?')}")
####################################################################################################################

# # test_faqs_prices.py
# import os
# from dotenv import load_dotenv
# load_dotenv()

# from app.integrations.palantir.foundry_service import _take_objects, flatten_osdk_object
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

#     # Check Hackathon object for faqs/prices fields
#     print("=" * 60)
#     print("HACKATHON 1 — ALL Properties:")
#     print("=" * 60)
#     hacks = client.ontology.objects.Hackathons.take(10)
#     h1 = next((h for h in hacks if getattr(h, "course_id", 0) == 1), None)
#     if h1:
#         for attr in sorted(dir(h1)):
#             if attr.startswith('__'):
#                 continue
#             try:
#                 val = getattr(h1, attr)
#                 val_type = type(val).__name__
#                 if val_type in ("method", "builtin_function_or_method", "function"):
#                     continue
#                 if not attr.startswith('_'):
#                     print(f"  {attr} ({val_type}) = {repr(val)[:250]}")
#             except Exception as e:
#                 print(f"  {attr} = [ERROR: {e}]")

#     # Try WinningPrize again
#     print("\n" + "=" * 60)
#     print("WINNING PRIZE:")
#     print("=" * 60)
#     try:
#         prizes = client.ontology.objects.WinningPrize.take(10)
#         print(f"  Found: {len(prizes)} items")
#         if prizes:
#             for p in prizes:
#                 for attr in sorted(dir(p)):
#                     if attr.startswith('__') or attr.startswith('_'):
#                         continue
#                     try:
#                         val = getattr(p, attr)
#                         val_type = type(val).__name__
#                         if val_type in ("method", "builtin_function_or_method", "function"):
#                             continue
#                         print(f"    {attr} ({val_type}) = {repr(val)[:200]}")
#                     except:
#                         pass
#                 print()
#     except Exception as e:
#         print(f"  ERROR: {e}")

#     # Check for FAQ object
#     print("\n" + "=" * 60)
#     print("CHECKING FAQ OBJECTS:")
#     print("=" * 60)
#     for name in ["Faq", "Faqs", "FAQ", "FAQs", "VanyarFaq", "HackathonFaq"]:
#         has_it = hasattr(client.ontology.objects, name)
#         if has_it:
#             print(f"  ⭐ {name}: EXISTS")
    
#     # Check all objects for anything with "faq" 
#     for attr in sorted(dir(client.ontology.objects)):
#         if 'faq' in attr.lower() and not attr.startswith('_'):
#             print(f"  ⭐ Found: {attr}")
###############################################################################################3

# # test_team_actions.py
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

#     print("ALL ACTIONS (checking for team-related):")
#     print("=" * 60)
#     for attr in sorted(dir(client.ontology.actions)):
#         if not attr.startswith('_'):
#             if 'team' in attr.lower() or 'join' in attr.lower() or 'member' in attr.lower():
#                 print(f"  ⭐ {attr}")
#                 try:
#                     sig = inspect.signature(getattr(client.ontology.actions, attr))
#                     print(f"      Params: {list(sig.parameters.keys())}")
#                 except:
#                     pass
#             else:
#                 print(f"  {attr}")

#########################################################################################################

# # test_team_full_check.py
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

#     # Search ALL objects for "team" related
#     print("=" * 60)
#     print("OBJECTS WITH 'TEAM' IN NAME:")
#     print("=" * 60)
#     for attr in sorted(dir(client.ontology.objects)):
#         if not attr.startswith('_'):
#             if 'team' in attr.lower():
#                 print(f"  ⭐ {attr}")

#     # Check VanyarTeam fully
#     print("\n" + "=" * 60)
#     print("VANYAR TEAM — ALL Properties + Methods:")
#     print("=" * 60)
#     teams = client.ontology.objects.VanyarTeam.take(5)
#     if teams:
#         t = teams[0]
#         for attr in sorted(dir(t)):
#             if attr.startswith('__'):
#                 continue
#             try:
#                 val = getattr(t, attr)
#                 val_type = type(val).__name__
#                 print(f"  {attr} ({val_type})")
#             except Exception as e:
#                 print(f"  {attr} = [ERROR: {e}]")

#     # Check ALL actions for anything team-related (broader search)
#     print("\n" + "=" * 60)
#     print("ALL ACTIONS (full list):")
#     print("=" * 60)
#     for attr in sorted(dir(client.ontology.actions)):
#         if not attr.startswith('_'):
#             print(f"  {attr}")

#     # Check VanyarEnrolment for team_id field
#     print("\n" + "=" * 60)
#     print("VANYAR ENROLMENT — Check for team_id:")
#     print("=" * 60)
#     enrollments = client.ontology.objects.VanyarEnrolment.take(5)
#     if enrollments:
#         e = enrollments[0]
#         for attr in sorted(dir(e)):
#             if attr.startswith('__'):
#                 continue
#             if 'team' in attr.lower():
#                 val = getattr(e, attr, None)
#                 print(f"  ⭐ {attr} = {val}")
######################################################################################################

import requests
from jose import jwt
from app.core.config import settings
import datetime

# Login
resp = requests.post("http://localhost:8000/api/auth/login", json={
    "email": "max@example.com",
    "password": "SecretPassword123"
})
data = resp.json()
print(f"Login response keys: {data.keys()}")

# Get token (camelCase from middleware)
token = data.get("accessToken") or data.get("access_token")
print(f"Token: {token[:50]}...")

# Decode
payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
print(f"Payload: {payload}")
print(f"Expires (exp): {payload.get('exp')}")

exp_time = datetime.datetime.fromtimestamp(payload['exp'])
now = datetime.datetime.now()
print(f"Expires at: {exp_time}")
print(f"Now: {now}")
print(f"Time left: {exp_time - now}")

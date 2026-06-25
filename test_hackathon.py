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
# test_team_object.py
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

    # Check for Team objects
    print("=" * 60)
    print("CHECKING TEAM-RELATED OBJECTS:")
    print("=" * 60)
    for name in ["Team", "Teams", "VanyarTeam", "HackathonTeam"]:
        has_it = hasattr(client.ontology.objects, name)
        print(f"  {name}: {'✅ EXISTS' if has_it else '❌ Not found'}")

    # Explore VanyarTeam (known)
    print("\n" + "=" * 60)
    print("VANYAR TEAM — ALL PROPERTIES:")
    print("=" * 60)
    teams = client.ontology.objects.VanyarTeam.take(10)
    print(f"  Found: {len(teams)} teams")
    if teams:
        t = teams[0]
        for attr in sorted(dir(t)):
            if attr.startswith('__'):
                continue
            try:
                val = getattr(t, attr)
                val_type = type(val).__name__
                if val_type in ("method", "builtin_function_or_method", "function"):
                    continue
                print(f"    {attr} ({val_type}) = {repr(val)[:200]}")
            except Exception as e:
                print(f"    {attr} = [ERROR: {e}]")

    # Check if "Team" exists separately
    if hasattr(client.ontology.objects, "Team"):
        print("\n" + "=" * 60)
        print("TEAM OBJECT (separate from VanyarTeam):")
        print("=" * 60)
        team_items = client.ontology.objects.Team.take(10)
        print(f"  Found: {len(team_items)} items")
        if team_items:
            for attr in sorted(dir(team_items[0])):
                if attr.startswith('__'):
                    continue
                try:
                    val = getattr(team_items[0], attr)
                    val_type = type(val).__name__
                    if val_type in ("method", "builtin_function_or_method", "function"):
                        continue
                    print(f"    {attr} ({val_type}) = {repr(val)[:200]}")
                except Exception as e:
                    print(f"    {attr} = [ERROR: {e}]")

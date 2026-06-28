# # test_progress_pk.py
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
#     items = client.ontology.objects.ProgressDetails.take(10)
#     print(f"Found: {len(items)} records\n")

#     for item in items:
#         print("Record:")
#         for attr in sorted(dir(item)):
#             if attr.startswith('__'):
#                 continue
#             try:
#                 val = getattr(item, attr)
#                 val_type = type(val).__name__
#                 if val_type in ("method", "builtin_function_or_method", "function"):
#                     continue
#                 if not attr.startswith('_'):
#                     print(f"  {attr} ({val_type}) = {repr(val)[:200]}")
#             except:
#                 pass
#         print()



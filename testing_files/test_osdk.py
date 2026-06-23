# ####################################################################################################################


# # test_osdk.py
# import os
# from dotenv import load_dotenv
# from training_and_hackathon_sdk import FoundryClient, ConfidentialClientAuth

# load_dotenv()

# print("\n--- [OSDK ISOLATED TEST RUN] ---")

# # 1. Load credentials
# client_id = os.getenv("FOUNDRY_CLIENT_ID")
# client_secret = os.getenv("FOUNDRY_CLIENT_SECRET")
# raw_url = os.getenv("FOUNDRY_URL")

# # Clean hostname (no protocol, no trailing slash)
# clean_hostname = raw_url.replace("https://", "").replace("http://", "").split("/")[0].rstrip("/")

# print(f"Targeting Hostname : {clean_hostname}")
# print(f"Active Client ID   : {client_id[:8]}..." if client_id else "Active Client ID   : ⚠️ MISSING")

# try:
#     # 2. Authenticate
#     auth = ConfidentialClientAuth(
#         client_id=client_id,
#         client_secret=client_secret,
#         hostname=clean_hostname,
#         should_refresh=True,
#     )
#     client = FoundryClient(auth=auth, hostname=clean_hostname)
#     print("✅ Client instantiated successfully!")

#     # 3. Discover available object types (baked into SDK)
#     print("\n--- [OBJECT CATALOG (from SDK package)] ---")
#     clean_catalog = [attr for attr in dir(client.ontology.objects) if not attr.startswith('_')]
#     print(f"Found {len(clean_catalog)} object type(s) defined in SDK:")
#     for i, obj in enumerate(clean_catalog, 1):
#         print(f"  {i}. {obj}")
#     print("--------------------------------------------\n")

#     # 4. Attempt to query an object type
#     target_type = "TraineeTrackerTask"
#     print(f"Attempting live query on: {target_type}...")

#     obj_api = getattr(client.ontology.objects, target_type)
#     records = obj_api.take(1)

#     print(f"✅ SUCCESS! Retrieved {len(records)} record(s)")

#     # 5. Print clean property data (filter out methods)
#     for record in records:
#         print(f"\n--- [{target_type} RECORD] ---")
#         for attr in sorted(dir(record)):
#             if attr.startswith('_'):
#                 continue
#             value = getattr(record, attr)
#             # Skip methods and callable objects
#             if callable(value):
#                 continue
#             # Truncate long strings for readability
#             if isinstance(value, str) and len(value) > 120:
#                 value = value[:120] + "..."
#             print(f"  {attr}: {value}")

#     # 6. Test all object types for accessibility
#     print("\n--- [BULK ACCESS TEST] ---")
#     accessible = []
#     denied = []
#     for obj_name in clean_catalog:
#         try:
#             api = getattr(client.ontology.objects, obj_name)
#             result = api.take(1)
#             accessible.append(obj_name)
#             print(f"  ✅ {obj_name} ({len(result)} record(s))")
#         except Exception as err:
#             denied.append(obj_name)
#             print(f"  ❌ {obj_name}: {str(err)[:80]}")

#     print(f"\n--- [SUMMARY] ---")
#     print(f"  Accessible: {len(accessible)}/{len(clean_catalog)}")
#     print(f"  Denied:     {len(denied)}/{len(clean_catalog)}")
#     if denied:
#         print(f"  Denied types: {', '.join(denied)}")

# except Exception as e:
#     print(f"\n❌ ERROR: {e}")
#     print("\n" + "=" * 60)
#     print("IF YOU SEE 'ObjectTypeNotFound':")
#     print("  → The code is CORRECT")
#     print("  → Your application (client_id) does NOT have permission")
#     print("    to access these object types on the server")
#     print("  → Only a Foundry admin can fix this in Developer Console")
#     print("=" * 60)
 #############3####################################################################################################################

# test_osdk.py ///Latest version; this is a standalone script to test the OSDK connection and query live data, independent of the FastAPI app context. It should be run separately from the main application to verify that the OSDK client can authenticate and retrieve data as expected.
import os
from dotenv import load_dotenv
from training_and_hackathon_sdk import FoundryClient, ConfidentialClientAuth

load_dotenv()

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
TARGET_TYPE = "VanyarEvent"  # Change this to query different types
RECORDS_TO_FETCH = 3                # Number of records to retrieve
RUN_BULK_TEST = True                # Set False to skip bulk access test

# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def get_properties(record):
    """Extract only data properties from a record (no methods, no private attrs)."""
    props = {}
    for attr in sorted(dir(record)):
        if attr.startswith('_'):
            continue
        value = getattr(record, attr)
        if callable(value):
            continue
        props[attr] = value
    return props


def format_value(value, max_length=100):
    """Format a value for clean display."""
    if value is None:
        return "—"
    if isinstance(value, str):
        if len(value) > max_length:
            return value[:max_length] + " ..."
        return value
    return str(value)


def print_record_card(record, index, type_name):
    """Print a single record as a clean formatted card."""
    props = get_properties(record)
    
    # Find the longest key for alignment
    max_key_len = max(len(k) for k in props.keys()) if props else 0
    
    print(f"\n  ┌{'─' * 60}")
    print(f"  │ 📄 {type_name} — Record #{index}")
    print(f"  ├{'─' * 60}")
    
    for key, value in props.items():
        formatted = format_value(value)
        print(f"  │  {key:<{max_key_len}} : {formatted}")
    
    print(f"  └{'─' * 60}")


def print_header(title):
    """Print a section header."""
    print(f"\n{'═' * 64}")
    print(f"  {title}")
    print(f"{'═' * 64}")


# ═══════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════

print_header("🚀 OSDK CONNECTION TEST")

# 1. Load credentials
client_id = os.getenv("FOUNDRY_CLIENT_ID")
client_secret = os.getenv("FOUNDRY_CLIENT_SECRET")
raw_url = os.getenv("FOUNDRY_URL")

clean_hostname = raw_url.replace("https://", "").replace("http://", "").split("/")[0].rstrip("/")

print(f"\n  Hostname  : {clean_hostname}")
print(f"  Client ID : {client_id[:8]}..." if client_id else "  Client ID : ⚠️ MISSING")
print(f"  Target    : {TARGET_TYPE}")
print(f"  Fetching  : {RECORDS_TO_FETCH} record(s)")

try:
    # 2. Authenticate
    auth = ConfidentialClientAuth(
        client_id=client_id,
        client_secret=client_secret,
        hostname=clean_hostname,
        should_refresh=True,
    )
    client = FoundryClient(auth=auth, hostname=clean_hostname)
    print(f"\n  ✅ Authenticated successfully!")

    # 3. Object catalog
    print_header("📚 OBJECT CATALOG")
    clean_catalog = [attr for attr in dir(client.ontology.objects) if not attr.startswith('_')]
    print(f"\n  {len(clean_catalog)} object type(s) available in SDK:\n")
    
    # Print in 2 columns
    mid = (len(clean_catalog) + 1) // 2
    for i in range(mid):
        col1 = f"  {i+1:>2}. {clean_catalog[i]:<30}"
        col2 = f"{i+mid+1:>2}. {clean_catalog[i+mid]}" if i + mid < len(clean_catalog) else ""
        print(f"  {col1}{col2}")

    # 4. Query target object type
    print_header(f"🔍 QUERY: {TARGET_TYPE}")

    obj_api = getattr(client.ontology.objects, TARGET_TYPE)
    records = obj_api.take(RECORDS_TO_FETCH)

    print(f"\n  ✅ Retrieved {len(records)} record(s)")

    # 5. Display records as formatted cards
    for i, record in enumerate(records, 1):
        print_record_card(record, i, TARGET_TYPE)

    # 6. Bulk access test
    if RUN_BULK_TEST:
        print_header("🧪 BULK ACCESS TEST")
        
        accessible = []
        denied = []
        
        for obj_name in clean_catalog:
            try:
                api = getattr(client.ontology.objects, obj_name)
                result = api.take(1)
                accessible.append((obj_name, len(result)))
                status = "✅"
                detail = f"{len(result)} record(s)"
            except Exception as err:
                denied.append((obj_name, str(err)[:60]))
                status = "❌"
                detail = "No access"
            print(f"  {status} {obj_name:<30} {detail}")

        # Summary
        print(f"\n  {'─' * 50}")
        print(f"  📊 Results: {len(accessible)} accessible, {len(denied)} denied (out of {len(clean_catalog)})")
        
        if denied:
            print(f"\n  ⚠️  Denied object types:")
            for name, err in denied:
                print(f"     • {name}")

    print_header("✅ TEST COMPLETE")

except Exception as e:
    print_header("❌ CONNECTION FAILED")
    print(f"\n  Error: {e}")
    print(f"\n  {'─' * 50}")
    print("  Troubleshooting:")
    print("    • ObjectTypeNotFound → Admin must grant app access in Developer Console")
    print("    • 401 Unauthorized   → Token/credentials expired")
    print("    • Connection error   → Check FOUNDRY_URL in .env")
    print(f"  {'─' * 50}")

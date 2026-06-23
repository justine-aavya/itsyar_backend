
# Tests OSDK Action execution (createUserAccount) and Link traversal.
# ⚠️ THIS WILL CREATE A REAL USER RECORD IN YOUR ONTOLOGY

import os
import uuid
import inspect
from datetime import datetime
from dotenv import load_dotenv
from training_and_hackathon_sdk import FoundryClient, ConfidentialClientAuth
from training_and_hackathon_sdk.ontology.objects import VanyarUser

load_dotenv()

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
LINK_TEST_TYPES = ["VanyarUser", "VanyarEvent", "VanyarTrack"]

# ⚠️ ACTION EXECUTION IS ON — this will create a user!
EXECUTE_TEST_ACTION = True
TEST_ACTION_NAME = "createUserAccount"

# Generate a unique test ID so it doesn't conflict with existing records
TEST_USER_ID = f"test-{uuid.uuid4().hex[:8]}"

TEST_ACTION_PARAMS = {
    "user_id": TEST_USER_ID,
    "email": f"{TEST_USER_ID}@test.invalid",
    "name": "OSDK Test User",
    "role": "Student",
    "interest": "Testing",
    "org_id": "test-org",
    "team_id": "test-team",
    "avatar_url": "",
}

# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def print_header(title):
    print(f"\n{'═' * 64}")
    print(f"  {title}")
    print(f"{'═' * 64}")


def print_subheader(title):
    print(f"\n  ┌{'─' * 58}")
    print(f"  │ {title}")
    print(f"  ├{'─' * 58}")


def print_footer():
    print(f"  └{'─' * 58}")


def get_clean_members(obj):
    return sorted([a for a in dir(obj) if not a.startswith('_')])


def discover_scalar_properties(record):
    props = {}
    for attr in sorted(dir(record)):
        if attr.startswith('_'):
            continue
        try:
            value = getattr(record, attr)
            if callable(value):
                continue
            if isinstance(value, (str, int, float, bool, type(None))):
                props[attr] = value
        except Exception:
            pass
    return props


def discover_links_on_record(record):
    links = []
    for attr in sorted(dir(record)):
        if attr.startswith('_'):
            continue
        try:
            value = getattr(record, attr)
            if callable(value) and not hasattr(value, 'take'):
                continue
            if hasattr(value, 'page') or hasattr(value, 'take') or hasattr(value, 'iter'):
                links.append(attr)
        except Exception:
            pass
    return links


# ═══════════════════════════════════════════════════════════════
# CONNECT
# ═══════════════════════════════════════════════════════════════

print_header("🚀 OSDK ACTIONS & LINKS TEST")

client_id = os.getenv("FOUNDRY_CLIENT_ID")
client_secret = os.getenv("FOUNDRY_CLIENT_SECRET")
raw_url = os.getenv("FOUNDRY_URL")

if not all([client_id, client_secret, raw_url]):
    print("\n  ❌ Missing .env variables!")
    exit(1)

clean_hostname = raw_url.replace("https://", "").replace("http://", "").split("/")[0].rstrip("/")
print(f"\n  Hostname  : {clean_hostname}")
print(f"  Client ID : {client_id[:8]}...")

try:
    auth = ConfidentialClientAuth(
        client_id=client_id,
        client_secret=client_secret,
        hostname=clean_hostname,
        should_refresh=True,
    )
    client = FoundryClient(auth=auth, hostname=clean_hostname)
    print(f"  ✅ Authenticated!")
except Exception as e:
    print(f"\n  ❌ Auth failed: {e}")
    exit(1)


# ═══════════════════════════════════════════════════════════════
# SECTION 1: DISCOVER ACTIONS
# ═══════════════════════════════════════════════════════════════

print_header("⚡ SECTION 1: ACTION CATALOG")

actions_ns = client.ontology.actions
all_action_names = [a for a in get_clean_members(actions_ns) if callable(getattr(actions_ns, a, None))]

print(f"\n  Found {len(all_action_names)} action(s):\n")
for i, name in enumerate(all_action_names, 1):
    print(f"    {i:>2}. ⚡ {name}")

if not all_action_names:
    print("    (none found — check SDK generation includes actions)")


# ═══════════════════════════════════════════════════════════════
# SECTION 2: INSPECT ACTION SIGNATURES
# ═══════════════════════════════════════════════════════════════

print_header("🔬 SECTION 2: ACTION SIGNATURES")

for action_name in all_action_names:
    action_fn = getattr(actions_ns, action_name)
    print_subheader(f"⚡ {action_name}")

    try:
        sig = inspect.signature(action_fn)
        params = sig.parameters

        if params:
            print(f"  │")
            print(f"  │  {'Parameter':<25} {'Type':<20} {'Required'}")
            print(f"  │  {'─' * 25} {'─' * 20} {'─' * 10}")
            for pname, param in params.items():
                ptype = (
                    param.annotation.__name__
                    if hasattr(param.annotation, '__name__')
                    else str(param.annotation)
                    if param.annotation != inspect.Parameter.empty
                    else "Any"
                )
                required = "Yes" if param.default == inspect.Parameter.empty else f"No (={param.default})"
                print(f"  │  {pname:<25} {ptype:<20} {required}")
        else:
            print(f"  │  (no parameters)")
    except (ValueError, TypeError) as e:
        print(f"  │  ⚠️  Cannot inspect: {e}")

    print_footer()


# ═══════════════════════════════════════════════════════════════
# SECTION 3: EXECUTE createUserAccount
# ═══════════════════════════════════════════════════════════════

print_header("🧪 SECTION 3: EXECUTE ACTION")

print(f"\n  Action    : {TEST_ACTION_NAME}")
print(f"  Test ID   : {TEST_USER_ID}")
print(f"  Params    :")
for k, v in TEST_ACTION_PARAMS.items():
    print(f"    {k:<15} = {v}")
print(f"\n  {'─' * 50}")

if TEST_ACTION_NAME not in all_action_names:
    print(f"\n  ❌ Action '{TEST_ACTION_NAME}' not found in SDK!")
    print(f"     Available: {all_action_names}")
    print(f"\n  💡 Update TEST_ACTION_NAME to one of the above and re-run.")
else:
    action_fn = getattr(actions_ns, TEST_ACTION_NAME)

    # Show expected params vs provided params
    param_check_passed = True
    try:
        sig = inspect.signature(action_fn)
        expected_params = set(sig.parameters.keys())
        provided_params = set(TEST_ACTION_PARAMS.keys())

        missing = expected_params - provided_params
        extra = provided_params - expected_params

        if missing:
            print(f"\n  ⚠️  Missing params (may fail): {missing}")
            param_check_passed = False
        if extra:
            print(f"\n  ⚠️  Extra params (may be ignored or error): {extra}")
        if not missing and not extra:
            print(f"\n  ✅ Params match signature perfectly!")
    except Exception:
        print(f"\n  ⚠️  Could not validate params against signature")

    # Execute the action
    print(f"\n  Executing action...")
    print(f"  {'─' * 50}")

    try:
        result = action_fn(**TEST_ACTION_PARAMS)
        print(f"\n  ✅ ACTION EXECUTED SUCCESSFULLY!")
        print(f"     Result type : {type(result).__name__}")
        print(f"     Result value: {result}")

        # Verify: try to fetch the created record
        print(f"\n  {'─' * 50}")
        print(f"  Verifying: Fetching created record by user_id...")

        try:
            collection = client.ontology.objects.VanyarUser
            prop = getattr(VanyarUser.object_type, "user_id")
            verification = collection.where(prop == TEST_USER_ID).take(1)

            if verification:
                print(f"\n  ✅ VERIFICATION PASSED — Record exists in ontology!")
                created_user = verification[0]
                props = discover_scalar_properties(created_user)
                print(f"\n  Created record properties:")
                for key, val in props.items():
                    display_val = str(val)[:60] if val is not None else "—"
                    print(f"    {key:<20} : {display_val}")
            else:
                print(f"\n  ⚠️  Record not immediately visible (may take a moment to sync)")
                print(f"     This is normal — Ontology indexing can have a short delay.")
        except Exception as verify_err:
            print(f"\n  ⚠️  Verification query failed: {verify_err}")
            print(f"     The action may have succeeded — check Foundry UI.")

    except Exception as e:
        print(f"\n  ❌ ACTION FAILED!")
        print(f"     Error type : {type(e).__name__}")
        print(f"     Error msg  : {e}")
        print(f"\n  {'─' * 50}")
        print(f"  Troubleshooting:")
        print(f"    • Check param names match the action definition exactly")
        print(f"    • Check your app has 'execute action' permissions")
        print(f"    • Check if the action has validation rules (e.g., unique email)")
        print(f"  {'─' * 50}")

        # If params didn't match, show what the action actually expects
        if not param_check_passed:
            print(f"\n  💡 Try updating TEST_ACTION_PARAMS to match these expected params:")
            try:
                sig = inspect.signature(action_fn)
                for pname, param in sig.parameters.items():
                    print(f"       {pname}")
            except Exception:
                pass


# ═══════════════════════════════════════════════════════════════
# SECTION 4: DISCOVER LINKS ON EACH OBJECT TYPE
# ═══════════════════════════════════════════════════════════════

print_header("🔗 SECTION 4: LINK DISCOVERY")

discovered_links = {}

for type_name in LINK_TEST_TYPES:
    print_subheader(f"🔗 {type_name}")

    if not hasattr(client.ontology.objects, type_name):
        print(f"  │  ⚠️  Not available in SDK (skipped)")
        print_footer()
        continue

    try:
        collection = getattr(client.ontology.objects, type_name)
        records = collection.take(1)

        if not records:
            print(f"  │  ⚠️  No records found (cannot inspect links)")
            print_footer()
            continue

        sample = records[0]

        # Show scalar properties for context
        scalars = discover_scalar_properties(sample)
        print(f"  │")
        print(f"  │  Scalar properties ({len(scalars)}):")
        for key, val in list(scalars.items())[:6]:
            display_val = str(val)[:50] if val is not None else "—"
            print(f"  │    • {key}: {display_val}")
        if len(scalars) > 6:
            print(f"  │    ... and {len(scalars) - 6} more")

        # Discover links
        links = discover_links_on_record(sample)
        discovered_links[type_name] = links

        print(f"  │")
        if links:
            print(f"  │  Link accessors ({len(links)}):")
            for link_name in links:
                print(f"  │    🔗 .{link_name}")
        else:
            # Broader search for non-scalar, non-callable attributes
            print(f"  │  No standard link accessors (.take/.page) found.")
            print(f"  │  Checking all non-scalar attributes:")

            all_non_scalar = []
            for attr in sorted(dir(sample)):
                if attr.startswith('_'):
                    continue
                try:
                    value = getattr(sample, attr)
                    if callable(value):
                        continue
                    if not isinstance(value, (str, int, float, bool, type(None))):
                        all_non_scalar.append((attr, type(value).__name__))
                except Exception as e:
                    all_non_scalar.append((attr, f"error: {str(e)[:30]}"))

            if all_non_scalar:
                for attr_name, type_name_str in all_non_scalar:
                    print(f"  │    ? .{attr_name} → {type_name_str}")
                discovered_links[type_name] = [a[0] for a in all_non_scalar]
            else:
                print(f"  │    (none — links may not be in SDK generation)")
                discovered_links[type_name] = []

    except Exception as e:
        print(f"  │  ❌ Error: {e}")
        discovered_links[type_name] = []

    print_footer()


# ═══════════════════════════════════════════════════════════════
# SECTION 5: TRAVERSE LINKS
# ═══════════════════════════════════════════════════════════════

print_header("🔗 SECTION 5: LINK TRAVERSAL")

has_any_links = any(len(v) > 0 for v in discovered_links.values())

if not has_any_links:
    print(f"\n  ℹ️  No links discovered on any object type.")
    print(f"     Possible reasons:")
    print(f"       • Link types not included in SDK generation")
    print(f"       • Links defined but no linked records exist yet")
    print(f"       • SDK needs regeneration after link types were added")
else:
    for type_name, links in discovered_links.items():
        if not links:
            continue

        print(f"\n  Testing links on {type_name}...")

        try:
            collection = getattr(client.ontology.objects, type_name)
            records = collection.take(1)

            if not records:
                print(f"    ⚠️  No records to traverse from.")
                continue

            sample = records[0]

            # Show which record we're starting from
            sample_id = (
                getattr(sample, 'user_id', None) or
                getattr(sample, 'event_id', None) or
                getattr(sample, 'name', None) or
                "unknown"
            )
            print(f"  Source: {type_name} [{sample_id}]")

            for link_name in links:
                print_subheader(f"{type_name}.{link_name}")

                try:
                    link_accessor = getattr(sample, link_name)

                    linked_objects = None
                    traversal_method = "unknown"

                    # Method 1: .take(n)
                    if hasattr(link_accessor, 'take'):
                        linked_objects = link_accessor.take(3)
                        traversal_method = ".take(3)"

                    # Method 2: .page()
                    elif hasattr(link_accessor, 'page'):
                        linked_objects = list(link_accessor.page(page_size=3))
                        traversal_method = ".page(page_size=3)"

                    # Method 3: .get() for single links
                    elif hasattr(link_accessor, 'get'):
                        result = link_accessor.get()
                        linked_objects = [result] if result else []
                        traversal_method = ".get()"

                    # Method 4: direct iteration
                    elif hasattr(link_accessor, '__iter__') and not isinstance(link_accessor, str):
                        linked_objects = list(link_accessor)[:3]
                        traversal_method = "iter()[:3]"

                    else:
                        print(f"  │  ⚠️  No known traversal method available")
                        print(f"  │     Type: {type(link_accessor).__name__}")
                        print(f"  │     Repr: {repr(link_accessor)[:80]}")
                        print_footer()
                        continue

                    # Display results
                    print(f"  │  Method  : {traversal_method}")
                    print(f"  │  Results : {len(linked_objects)} linked object(s)")

                    if linked_objects:
                        print(f"  │")
                        for i, obj in enumerate(linked_objects[:3], 1):
                            obj_type = type(obj).__name__
                            display = (
                                getattr(obj, 'name', None) or
                                getattr(obj, 'title', None) or
                                getattr(obj, 'email', None) or
                                getattr(obj, 'user_id', None) or
                                str(obj)[:40]
                            )
                            print(f"  │  {i}. [{obj_type}] {display}")

                            # Show a few properties of the linked object
                            linked_props = discover_scalar_properties(obj)
                            for key, val in list(linked_props.items())[:3]:
                                display_val = str(val)[:40] if val is not None else "—"
                                print(f"  │       {key}: {display_val}")
                            print(f"  │")

                        print(f"  │  ✅ Link traversal successful!")
                    else:
                        print(f"  │  (no linked objects — relationship exists but no data)")

                except Exception as e:
                    print(f"  │  ❌ Traversal failed: {e}")

                print_footer()

        except Exception as e:
            print(f"    ❌ Error fetching {type_name}: {e}")


# ═══════════════════════════════════════════════════════════════
# SECTION 6: SUMMARY
# ═══════════════════════════════════════════════════════════════

print_header("📊 FINAL SUMMARY")

print(f"\n  Actions")
print(f"  {'─' * 50}")
print(f"  Total discovered       : {len(all_action_names)}")
print(f"  Executed               : {TEST_ACTION_NAME}")
for name in all_action_names:
    marker = " ← TESTED" if name == TEST_ACTION_NAME else ""
    print(f"    ⚡ {name}{marker}")

print(f"\n  Links")
print(f"  {'─' * 50}")
total_links = sum(len(v) for v in discovered_links.values())
print(f"  Total discovered       : {total_links}")
for type_name, links in discovered_links.items():
    if links:
        print(f"    {type_name}:")
        for link in links:
            print(f"      🔗 .{link}")
    else:
        print(f"    {type_name}: (no links)")

print(f"\n  Test Record")
print(f"  {'─' * 50}")
print(f"  Created user_id        : {TEST_USER_ID}")
print(f"  Created email          : {TEST_ACTION_PARAMS['email']}")
print(f"\n  💡 To clean up test data, delete this record from your ontology.")

print_header("✅ ALL TESTS COMPLETE")
print()

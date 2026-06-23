# test_osdk_actions_links.py
# Standalone script to test OSDK Action types and Link types.
# Verifies that action definitions are accessible and link traversal works.
# Run independently from the FastAPI app context.

import os
from dotenv import load_dotenv
from training_and_hackathon_sdk import FoundryClient, ConfidentialClientAuth

load_dotenv()

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
# Object type to use for link traversal testing
LINK_SOURCE_TYPE = "Courses"
LINK_SOURCE_FETCH = 2  # Records to fetch for link testing

# Set to True to attempt a dry-run action call (no actual mutations)
RUN_ACTION_DRY_RUN = False  # ⚠️ Set True only if you have a safe test action

# If RUN_ACTION_DRY_RUN is True, configure the test action here:
DRY_RUN_ACTION_NAME = "createUserAccount"
DRY_RUN_ACTION_PARAMS = {
    "id": "test-dry-run-00000",
    "email": "dryrun@test.invalid",
    "password": "not-a-real-hash",
    "fullName": "Dry Run Test",
    "role": "Student",
}


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

def get_public_attrs(obj):
    """Get non-private, non-callable attributes of an object."""
    return sorted([
        attr for attr in dir(obj)
        if not attr.startswith('_') and not callable(getattr(obj, attr, None))
    ])


def get_public_methods(obj):
    """Get non-private callable attributes (methods) of an object."""
    return sorted([
        attr for attr in dir(obj)
        if not attr.startswith('_') and callable(getattr(obj, attr, None))
    ])


def get_link_properties(record):
    """
    Identify link-like attributes on a record.
    Links are typically callable properties or have specific OSDK types.
    """
    links = []
    for attr in sorted(dir(record)):
        if attr.startswith('_'):
            continue
        try:
            value = getattr(record, attr)
            # Links in OSDK are typically accessor objects (not plain values)
            # They usually have methods like .get(), .page(), .take(), .where()
            if hasattr(value, 'page') or hasattr(value, 'take') or hasattr(value, 'get'):
                links.append(attr)
        except Exception:
            continue
    return links


def format_value(value, max_length=80):
    """Format a value for clean display."""
    if value is None:
        return "—"
    if isinstance(value, str):
        return value[:max_length] + " ..." if len(value) > max_length else value
    if isinstance(value, list):
        return f"[{len(value)} items]"
    return str(value)[:max_length]


def print_header(title):
    """Print a section header."""
    print(f"\n{'═' * 64}")
    print(f"  {title}")
    print(f"{'═' * 64}")


def print_subheader(title):
    """Print a subsection header."""
    print(f"\n  ┌{'─' * 58}")
    print(f"  │ {title}")
    print(f"  ├{'─' * 58}")


# ═══════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════

print_header("🚀 OSDK ACTIONS & LINKS TEST")

# 1. Load credentials
client_id = os.getenv("FOUNDRY_CLIENT_ID")
client_secret = os.getenv("FOUNDRY_CLIENT_SECRET")
raw_url = os.getenv("FOUNDRY_URL")

if not all([client_id, client_secret, raw_url]):
    print("\n  ❌ Missing environment variables. Check .env file.")
    print("     Required: FOUNDRY_CLIENT_ID, FOUNDRY_CLIENT_SECRET, FOUNDRY_URL")
    exit(1)

clean_hostname = raw_url.replace("https://", "").replace("http://", "").split("/")[0].rstrip("/")

print(f"\n  Hostname       : {clean_hostname}")
print(f"  Client ID      : {client_id[:8]}..." if client_id else "  Client ID : ⚠️ MISSING")
print(f"  Link Source    : {LINK_SOURCE_TYPE}")
print(f"  Dry-Run Action : {'Enabled' if RUN_ACTION_DRY_RUN else 'Disabled'}")

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

    # ═══════════════════════════════════════════════════════════
    # SECTION A: ACTION TYPE CATALOG
    # ═══════════════════════════════════════════════════════════
    print_header("⚡ ACTION TYPE CATALOG")

    actions_namespace = client.ontology.actions
    action_names = [
        attr for attr in sorted(dir(actions_namespace))
        if not attr.startswith('_')
    ]

    # Filter to callable actions only
    callable_actions = []
    non_callable = []
    for name in action_names:
        member = getattr(actions_namespace, name, None)
        if callable(member):
            callable_actions.append(name)
        else:
            non_callable.append(name)

    print(f"\n  {len(callable_actions)} action type(s) available in SDK:\n")

    for i, action_name in enumerate(callable_actions, 1):
        print(f"    {i:>2}. ⚡ {action_name}")

    if non_callable:
        print(f"\n  ({len(non_callable)} non-callable attribute(s) skipped)")

    # ═══════════════════════════════════════════════════════════
    # SECTION B: ACTION INSPECTION
    # ═══════════════════════════════════════════════════════════
    print_header("🔬 ACTION INSPECTION")

    for action_name in callable_actions:
        action_fn = getattr(actions_namespace, action_name)
        print_subheader(f"⚡ {action_name}")

        # Try to get function signature / docstring
        import inspect
        try:
            sig = inspect.signature(action_fn)
            params = list(sig.parameters.keys())
            if params:
                for param_name in params:
                    param = sig.parameters[param_name]
                    annotation = param.annotation if param.annotation != inspect.Parameter.empty else "Any"
                    default = param.default if param.default != inspect.Parameter.empty else "required"
                    print(f"  │  param: {param_name:<20} type: {str(annotation):<20} default: {default}")
            else:
                print(f"  │  (no parameters detected in signature)")
        except (ValueError, TypeError):
            print(f"  │  (signature inspection not available)")

        # Docstring
        doc = getattr(action_fn, '__doc__', None)
        if doc:
            print(f"  │  doc: {doc.strip()[:80]}")

        print(f"  └{'─' * 58}")

    # ═══════════════════════════════════════════════════════════
    # SECTION C: ACTION DRY-RUN TEST
    # ═══════════════════════════════════════════════════════════
    if RUN_ACTION_DRY_RUN:
        print_header("🧪 ACTION DRY-RUN TEST")
        print(f"\n  Action : {DRY_RUN_ACTION_NAME}")
        print(f"  Params : {DRY_RUN_ACTION_PARAMS}")

        if DRY_RUN_ACTION_NAME not in callable_actions:
            print(f"\n  ❌ Action '{DRY_RUN_ACTION_NAME}' not found in SDK.")
            print(f"     Available: {callable_actions}")
        else:
            try:
                # Attempt to validate the action (some SDKs support validate mode)
                action_fn = getattr(actions_namespace, DRY_RUN_ACTION_NAME)

                # Check if validate/preview mode exists
                if hasattr(action_fn, 'validate'):
                    result = action_fn.validate(**DRY_RUN_ACTION_PARAMS)
                    print(f"\n  ✅ Validation passed!")
                    print(f"     Result: {result}")
                else:
                    # ⚠️ This WILL execute the action — only use with truly safe test data
                    print(f"\n  ⚠️  No validate mode available. Executing action...")
                    result = action_fn(**DRY_RUN_ACTION_PARAMS)
                    print(f"\n  ✅ Action executed successfully!")
                    print(f"     Result: {result}")

            except Exception as e:
                error_msg = str(e)
                if "validation" in error_msg.lower() or "invalid" in error_msg.lower():
                    print(f"\n  ⚠️  Validation error (expected for dry-run): {error_msg[:100]}")
                else:
                    print(f"\n  ❌ Action failed: {error_msg[:150]}")
    else:
        print_header("⏭️  ACTION DRY-RUN SKIPPED")
        print(f"\n  Set RUN_ACTION_DRY_RUN = True to test action execution.")
        print(f"  ⚠️  Warning: This will MUTATE data if no validate mode exists.")

    # ═══════════════════════════════════════════════════════════
    # SECTION D: LINK TYPE DISCOVERY
    # ═══════════════════════════════════════════════════════════
    print_header(f"🔗 LINK TYPE DISCOVERY ({LINK_SOURCE_TYPE})")

    if not hasattr(client.ontology.objects, LINK_SOURCE_TYPE):
        print(f"\n  ❌ Object type '{LINK_SOURCE_TYPE}' not found in SDK.")
        print(f"     Available: {[a for a in dir(client.ontology.objects) if not a.startswith('_')]}")
    else:
        obj_api = getattr(client.ontology.objects, LINK_SOURCE_TYPE)
        records = obj_api.take(LINK_SOURCE_FETCH)

        if not records:
            print(f"\n  ⚠️  No records found for '{LINK_SOURCE_TYPE}'. Cannot test links.")
        else:
            print(f"\n  ✅ Fetched {len(records)} record(s) to inspect links.\n")

            sample = records[0]

            # Method 1: Discover link-like attributes (have .page/.take/.get)
            link_attrs = get_link_properties(sample)

            # Method 2: Check all attributes and identify non-scalar ones
            all_attrs = sorted(dir(sample))
            scalar_props = {}
            link_candidates = []

            for attr in all_attrs:
                if attr.startswith('_'):
                    continue
                try:
                    value = getattr(sample, attr)
                    if callable(value):
                        continue
                    # Scalars: str, int, float, bool, None, date, datetime
                    if isinstance(value, (str, int, float, bool, type(None))):
                        scalar_props[attr] = value
                    else:
                        link_candidates.append((attr, type(value).__name__))
                except Exception as e:
                    link_candidates.append((attr, f"error: {str(e)[:40]}"))

            # Display discovered links
            if link_attrs:
                print(f"  🔗 Link accessors (have .page/.take/.get):\n")
                for link_name in link_attrs:
                    print(f"    • {link_name}")
            else:
                print(f"  ℹ️  No link accessors with .page/.take/.get found.")

            if link_candidates:
                print(f"\n  🔗 Non-scalar attributes (potential links):\n")
                for attr_name, type_name in link_candidates:
                    print(f"    • {attr_name:<30} type: {type_name}")

            if not link_attrs and not link_candidates:
                print(f"  ℹ️  No link properties detected on {LINK_SOURCE_TYPE}.")
                print(f"      This may mean links are accessed differently in your SDK version.")

    # ═══════════════════════════════════════════════════════════
    # SECTION E: LINK TRAVERSAL TEST
    # ═══════════════════════════════════════════════════════════
    print_header("🔗 LINK TRAVERSAL TEST")

    if not hasattr(client.ontology.objects, LINK_SOURCE_TYPE):
        print(f"\n  Skipped — source type not available.")
    else:
        obj_api = getattr(client.ontology.objects, LINK_SOURCE_TYPE)
        records = obj_api.take(LINK_SOURCE_FETCH)

        if not records:
            print(f"\n  Skipped — no records available.")
        else:
            sample = records[0]
            link_attrs = get_link_properties(sample)

            if not link_attrs:
                print(f"\n  ℹ️  No traversable links found on {LINK_SOURCE_TYPE} records.")
                print(f"      Try setting LINK_SOURCE_TYPE to an object with known relationships.")
            else:
                for link_name in link_attrs:
                    print_subheader(f"🔗 {LINK_SOURCE_TYPE} → .{link_name}")

                    try:
                        link_accessor = getattr(sample, link_name)

                        # Try .take() for multi-links
                        if hasattr(link_accessor, 'take'):
                            linked_objects = link_accessor.take(3)
                            print(f"  │  Type     : Multi-link (collection)")
                            print(f"  │  Results  : {len(linked_objects)} linked object(s)")

                            for i, linked_obj in enumerate(linked_objects[:3], 1):
                                obj_type = type(linked_obj).__name__
                                # Try to get a display identifier
                                display_id = (
                                    getattr(linked_obj, 'id', None)
                                    or getattr(linked_obj, 'name', None)
                                    or getattr(linked_obj, 'title', None)
                                    or str(linked_obj)[:50]
                                )
                                print(f"  │    {i}. [{obj_type}] {display_id}")

                        # Try .get() for single-links
                        elif hasattr(link_accessor, 'get'):
                            linked_obj = link_accessor.get()
                            if linked_obj:
                                obj_type = type(linked_obj).__name__
                                display_id = (
                                    getattr(linked_obj, 'id', None)
                                    or getattr(linked_obj, 'name', None)
                                    or str(linked_obj)[:50]
                                )
                                print(f"  │  Type     : Single-link")
                                print(f"  │  Target   : [{obj_type}] {display_id}")
                            else:
                                print(f"  │  Type     : Single-link")
                                print(f"  │  Target   : (empty / null)")

                        else:
                            print(f"  │  Type     : Unknown accessor pattern")
                            print(f"  │  Value    : {repr(link_accessor)[:80]}")

                    except Exception as e:
                        print(f"  │  ❌ Error : {str(e)[:80]}")

                    print(f"  └{'─' * 58}")

    # ═══════════════════════════════════════════════════════════
    # SECTION F: BULK ACTION ACCESS TEST
    # ═══════════════════════════════════════════════════════════
    print_header("🧪 BULK ACTION ACCESS SUMMARY")

    accessible_actions = []
    denied_actions = []

    for action_name in callable_actions:
        try:
            action_fn = getattr(actions_namespace, action_name)
            # Just verify it's callable and accessible — don't execute
            if callable(action_fn):
                accessible_actions.append(action_name)
                status_icon = "✅"
            else:
                denied_actions.append((action_name, "not callable"))
                status_icon = "⚠️"
        except Exception as e:
            denied_actions.append((action_name, str(e)[:60]))
            status_icon = "❌"
        print(f"  {status_icon} {action_name}")

    print(f"\n  {'─' * 50}")
    print(f"  📊 Actions: {len(accessible_actions)} accessible, {len(denied_actions)} issues")

    # ═══════════════════════════════════════════════════════════
    # DONE
    # ═══════════════════════════════════════════════════════════
    print_header("✅ ACTIONS & LINKS TEST COMPLETE")

    print(f"\n  Summary:")
    print(f"    • Action types discovered : {len(callable_actions)}")
    print(f"    • Link attributes found   : {len(link_attrs) if 'link_attrs' in dir() else 'N/A'}")
    print(f"    • Dry-run executed        : {'Yes' if RUN_ACTION_DRY_RUN else 'No'}")
    print()

except Exception as e:
    print_header("❌ TEST FAILED")
    print(f"\n  Error: {e}")
    import traceback
    traceback.print_exc()
    print(f"\n  {'─' * 50}")
    print("  Troubleshooting:")
    print("    • ObjectTypeNotFound    → Admin must grant app access in Developer Console")
    print("    • 401 Unauthorized      → Token/credentials expired or scopes missing")
    print("    • ActionNotFound        → Action type not published or app lacks permissions")
    print("    • LinkPropertyError     → Link type not included in SDK generation")
    print("    • Connection error      → Check FOUNDRY_URL in .env")
    print(f"  {'─' * 50}")

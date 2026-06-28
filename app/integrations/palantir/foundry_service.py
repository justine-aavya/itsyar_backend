
# app/integrations/palantir/foundry_service.py
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import urllib.parse

from app.integrations.palantir.foundry_client import (
    foundry_osdk, is_foundry_configured
)


# ═══════════════════════════════════════════════════════════════
# OSDK IMPORTS
# ═══════════════════════════════════════════════════════════════

try:
    from training_and_hackathon_sdk.ontology.objects import VanyarUser
except ImportError:
    VanyarUser = None

try:
    from training_and_hackathon_sdk.ontology.objects import VanyarEvent
except ImportError:
    VanyarEvent = None

try:
    from training_and_hackathon_sdk.ontology.objects import VanyarTrack
except ImportError:
    VanyarTrack = None

try:
    from training_and_hackathon_sdk.ontology.objects import VanyarChallenge
except ImportError:
    VanyarChallenge = None

try:
    from training_and_hackathon_sdk.ontology.objects import VanyarLeaderboardEntry
except ImportError:
    VanyarLeaderboardEntry = None

try:
    from training_and_hackathon_sdk.ontology.objects import Hackathons
except ImportError:
    Hackathons = None

try:
    from training_and_hackathon_sdk.ontology.objects import Courses
except ImportError:
    Courses = None

try:
    from training_and_hackathon_sdk.ontology.objects import ReviewsFeedback
except ImportError:
    ReviewsFeedback = None

try:
    from training_and_hackathon_sdk.ontology.objects import VanyarEnrolment
except ImportError:
    VanyarEnrolment = None

try:
    from training_and_hackathon_sdk.ontology.objects import Quizes
except ImportError:
    Quizes = None


try:
    from foundry_sdk_runtime import AllowBetaFeatures
except ImportError:
    @contextmanager
    def AllowBetaFeatures():
        yield


# ═══════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════

_OSDK_INTERNAL_ATTRS = {
    "object_type", "rid", "modified_properties", "primary_key",
    "api_name", "properties", "links"
}

_SKIP_TYPES = {"method", "builtin_function_or_method", "function"}


def _take_objects(type_name: str, count: int = 200) -> list:
    """Fetch objects with AllowBetaFeatures enabled."""
    with AllowBetaFeatures():
        client = foundry_osdk.get_client()
        if not hasattr(client.ontology.objects, type_name):
            return []
        return getattr(client.ontology.objects, type_name).take(count)


def flatten_osdk_object(obj) -> Dict[str, Any]:
    """Convert an OSDK object to a plain dictionary."""
    if not obj:
        return {}
    if isinstance(obj, dict):
        return obj.copy()
    if isinstance(obj, list):
        return flatten_osdk_object(obj[0]) if obj else {}

    data = {}
    for attr in sorted(dir(obj)):
        if attr.startswith('_'):
            continue
        if attr in _OSDK_INTERNAL_ATTRS:
            continue

        try:
            value = getattr(obj, attr)
            val_type = type(value).__name__

            if val_type in _SKIP_TYPES:
                continue
            if hasattr(value, 'take') or hasattr(value, 'page'):
                continue

            if value is None:
                data[attr] = None
            elif isinstance(value, (str, int, float, bool)):
                data[attr] = value
            elif isinstance(value, (list, dict)):
                data[attr] = value
            elif hasattr(value, 'isoformat'):
                data[attr] = value.isoformat()
            else:
                data[attr] = str(value)

        except Exception:
            continue

    # Normalize ID
    if "id" not in data:
        for pk in ["event_id", "user_id", "track_id", "challenge_id", "course_id", "enrolment_id"]:
            if pk in data:
                data["id"] = data[pk]
                break

    # Normalize title/name
        # Normalize title/name
    if "title" not in data:
        if "name" in data:
            data["title"] = data["name"]
        elif "course_name1" in data:
            data["title"] = data["course_name1"]
            data["name"] = data["course_name1"]

    # Normalize duration
    if "duration" not in data and "duration1" in data:
        data["duration"] = data["duration1"]

    return data


def _build_video_proxy_url(raw_foundry_url: str) -> str:
    """Return the original Foundry URL for iframe embedding on frontend."""
    return raw_foundry_url or ""

# def get_course_thumbnail_content(course_id: str) -> tuple:
#     """Fetch thumbnail image from Foundry using OSDK media property."""
#     if not is_foundry_configured():
#         return (None, None)

#     try:
#         try:
#             pk_value = int(course_id)
#         except ValueError:
#             pk_value = course_id

#         with AllowBetaFeatures():
#             client = foundry_osdk.get_client()
#             course_obj = client.ontology.objects.Courses.get(pk_value)
#             media_stream = course_obj.image.get_media_content()
#             content = media_stream.read()

#         return (content, "image/jpeg")

#     except Exception as e:
#         print(f"[FOUNDRY ERROR] Thumbnail fetch failed: {str(e)}")
#         return (None, None)


# for multiple courses
def get_course_thumbnail_content(course_id: str) -> tuple:
    """Fetch thumbnail image from Foundry (same for all modules in a course)."""
    if not is_foundry_configured():
        return (None, None)

    try:
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            all_courses = client.ontology.objects.Courses.take(200)

            # Get first record for this course (thumbnail is same for all lessons)
            target = next(
                (c for c in all_courses if str(getattr(c, "course_id", "")) == str(course_id)),
                None
            )

            if not target:
                return (None, None)

            media_stream = target.image.get_media_content()
            content = media_stream.read()

        return (content, "image/jpeg")

    except Exception as e:
        print(f"[FOUNDRY ERROR] Thumbnail fetch failed: {str(e)}")
        return (None, None)



def apply_effective_status(event_data: dict) -> dict:
    """Derive effective status from event dates."""
    if not isinstance(event_data, dict):
        return event_data

    stored_status = str(event_data.get("status", "")).upper()
    if stored_status in ["DRAFT", "CANCELLED"]:
        return event_data
    if stored_status == "UPCOMING":
        stored_status = "PUBLISHED"

    start_date = event_data.get("start_date") or event_data.get("startDate")
    end_date = event_data.get("end_date") or event_data.get("endDate")

    if start_date and end_date:
        try:
            now = datetime.utcnow()
            start = datetime.fromisoformat(str(start_date).replace("Z", "").replace("+00:00", ""))
            end = datetime.fromisoformat(str(end_date).replace("Z", "").replace("+00:00", ""))
            if now > end:
                event_data["status"] = "COMPLETED"
            elif start <= now <= end:
                event_data["status"] = "ACTIVE"
            else:
                event_data["status"] = stored_status
        except ValueError:
            event_data["status"] = stored_status
    else:
        event_data["status"] = stored_status

    if not event_data.get("title"):
        event_data["title"] = event_data.get("name", "Untitled Event")

    return event_data


def get_mock_events() -> list:
    return [
        {"id": "evt_mock_1", "title": "Orion Hackathon Alpha", "description": "Enterprise-wide data streaming simulation.", "status": "ACTIVE", "startDate": "2026-01-01T00:00:00Z", "endDate": "2026-12-31T23:59:59Z", "eventType": "Analytical", "orgId": "demo-org"},
        {"id": "evt_mock_2", "title": "Vanyar Code Sprint Beta", "description": "Algorithmic execution matrix optimization.", "status": "PUBLISHED", "startDate": "2026-08-01T00:00:00Z", "endDate": "2026-08-15T23:59:59Z", "eventType": "Algorithmic", "orgId": "demo-org"},
        {"id": "evt_mock_3", "title": "Legacy Data Engine Challenge", "description": "Historical predictive model training.", "status": "COMPLETED", "startDate": "2025-01-01T00:00:00Z", "endDate": "2025-01-10T23:59:59Z", "eventType": "Predictive", "orgId": "demo-org"},
    ]


def get_mock_tracks() -> list:
    return [
        {"id": "track_mock_1", "name": "Artificial Intelligence & ML Graphs", "moduleCount": 8, "description": "Deep-dive neural network architecture."},
        {"id": "track_mock_2", "name": "Enterprise Cloud Architecture & DevOps", "moduleCount": 5, "description": "High-availability deployment setups."},
    ]


# ═══════════════════════════════════════════════════════════════
# EVENTS
# ═══════════════════════════════════════════════════════════════

def get_all_events(status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    if not is_foundry_configured():
        fallback = get_mock_events()
        if status_filter:
            requested = [s.strip().upper() for s in status_filter.split(",")]
            return [e for e in fallback if str(e.get("status", "")).upper() in requested]
        return fallback

    try:
        raw_events = _take_objects("VanyarEvent", 100)
        events_list = [apply_effective_status(flatten_osdk_object(obj)) for obj in raw_events]

        if status_filter:
            requested = [s.strip().upper() for s in status_filter.split(",")]
            return [e for e in events_list if str(e.get("status", "")).upper() in requested]
        return events_list

    except Exception as e:
        print(f"[FOUNDRY WARNING] Events fetch failed: {str(e)}")
        return get_mock_events()


def get_event_by_id(event_id: str) -> Optional[Dict[str, Any]]:
    if not is_foundry_configured():
        return next((e for e in get_mock_events() if e["id"] == event_id), None)

    try:
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            try:
                raw_event = client.ontology.objects.VanyarEvent.get(event_id)
                return apply_effective_status(flatten_osdk_object(raw_event))
            except Exception:
                pass

            if VanyarEvent is not None:
                for pk_name in ["event_id", "id", "eventId"]:
                    if hasattr(VanyarEvent.object_type, pk_name):
                        prop = getattr(VanyarEvent.object_type, pk_name)
                        results = client.ontology.objects.VanyarEvent.where(prop == event_id).take(1)
                        if results:
                            return apply_effective_status(flatten_osdk_object(results[0]))
        return None

    except Exception as e:
        print(f"[FOUNDRY ERROR] Event {event_id} fetch failed: {str(e)}")
        return None


# ═══════════════════════════════════════════════════════════════
# CHALLENGES
# ═══════════════════════════════════════════════════════════════

def get_challenges(event_id: str) -> List[Dict[str, Any]]:
    if not is_foundry_configured():
        return []

    try:
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            if not hasattr(client.ontology.objects, "VanyarChallenge"):
                return []

            if VanyarChallenge is not None and hasattr(VanyarChallenge.object_type, "event_id"):
                prop = getattr(VanyarChallenge.object_type, "event_id")
                results = client.ontology.objects.VanyarChallenge.where(prop == event_id).take(50)
            else:
                all_challenges = client.ontology.objects.VanyarChallenge.take(200)
                results = [c for c in all_challenges if getattr(c, "event_id", None) == event_id]

        return [flatten_osdk_object(c) for c in results]

    except Exception as e:
        print(f"[FOUNDRY ERROR] Challenges fetch failed: {str(e)}")
        return []


# ═══════════════════════════════════════════════════════════════
# TRACKS
# ═══════════════════════════════════════════════════════════════

def get_all_tracks() -> List[Dict[str, Any]]:
    if not is_foundry_configured():
        return get_mock_tracks()

    try:
        raw_tracks = _take_objects("VanyarTrack", 50)
        return [flatten_osdk_object(item) for item in raw_tracks]
    except Exception as e:
        print(f"[FOUNDRY ERROR] Tracks fetch failed: {str(e)}")
        return get_mock_tracks()

######################################################################################################
# # ═══════════════════════════════════════════════════════════════
# # COURSES — LIST, SEARCH, DETAIL
# # ═══════════════════════════════════════════════════════════════

### Single course, after multi-module
def get_all_courses(
    offset: int = 0,
    limit: int = 6,
    category: Optional[str] = None,
    level: Optional[str] = None
) -> Dict[str, Any]:
    """List all courses with pagination and optional filters."""
    if not is_foundry_configured():
        return {"courses": [], "total": 0, "offset": offset, "limit": limit}

    try:
        raw = _take_objects("Courses", 200)

        # Deduplicate by course_id (multiple lessons per course)
        seen = {}
        for c in raw:
            cid = str(getattr(c, "course_id", ""))
            if cid not in seen:
                seen[cid] = c
        courses = [flatten_osdk_object(c) for c in seen.values()]

        # Apply category filter
        if category:
            courses = [c for c in courses if str(c.get("tag", "")).lower() == category.lower()]

        # Apply level filter
        if level:
            courses = [c for c in courses if str(c.get("level", "")).lower() == level.lower()]

        # Calculate total before pagination
        total = len(courses)

        # Apply pagination
        paginated = courses[offset:offset + limit]

        # Format each course
        formatted = []
        for c in paginated:
            formatted.append({
                "id": str(c.get("course_id", c.get("id", ""))),
                "title": c.get("title") or c.get("course_name1", "Untitled"),
                "tag": c.get("tag", "General"),
                "duration": c.get("duration") or c.get("duration1", "Self-paced"),
                "instructor": c.get("instructor", "ItsYar Team"),
                "description": c.get("description", ""),
                "image": f"/api/courses/thumbnail/{c.get('course_id', c.get('id', ''))}",
                "badge": c.get("badge"),
                "level": c.get("level", "Beginner"),
            })

        return {"courses": formatted, "total": total, "offset": offset, "limit": limit}

    except Exception as e:
        print(f"[FOUNDRY ERROR] Courses fetch failed: {str(e)}")
        return {"courses": [], "total": 0, "offset": offset, "limit": limit}


### Singel Course, before multi-module update
# def get_all_courses(
#     offset: int = 0,
#     limit: int = 6,
#     category: Optional[str] = None,
#     level: Optional[str] = None
# ) -> Dict[str, Any]:
#     """List all courses with pagination and optional filters."""
#     if not is_foundry_configured():
#         return {"courses": [], "total": 0, "offset": offset, "limit": limit}

#     try:
#         raw = _take_objects("Courses", 200)
#         courses = [flatten_osdk_object(c) for c in raw]

#         # Apply category filter
#         if category:
#             courses = [c for c in courses if str(c.get("tag", "")).lower() == category.lower()]

#         # Apply level filter
#         if level:
#             courses = [c for c in courses if str(c.get("level", "")).lower() == level.lower()]

#         # Calculate total before pagination
#         total = len(courses)

#         # Apply pagination
#         paginated = courses[offset:offset + limit]

#         # Format each course
#         formatted = []
#         for c in paginated:
#             formatted.append({
#                 "id": str(c.get("course_id", c.get("id", ""))),
#                 "title": c.get("title") or c.get("course_name1", "Untitled"),
#                 "tag": c.get("tag", "General"),
#                 "duration": c.get("duration") or c.get("duration1", "Self-paced"),
#                 "instructor": c.get("instructor", "ItsYar Team"),
#                 "description": c.get("description", ""),
#                 "image": f"/api/courses/thumbnail/{c.get('course_id', c.get('id', ''))}",
#                 "badge": c.get("badge"),
#                 "level": c.get("level", "Beginner"),
#             })

#         return {"courses": formatted, "total": total, "offset": offset, "limit": limit}

#     except Exception as e:
#         print(f"[FOUNDRY ERROR] Courses fetch failed: {str(e)}")
#         return {"courses": [], "total": 0, "offset": offset, "limit": limit}

#For multiple courses
# def get_all_courses(
#     offset: int = 0,
#     limit: int = 6,
#     category: Optional[str] = None,
#     level: Optional[str] = None
# ) -> Dict[str, Any]:
#     """List all courses with pagination (deduplicated by course_id)."""
#     if not is_foundry_configured():
#         return {"courses": [], "total": 0, "offset": offset, "limit": limit}

#     try:
#         raw = _take_objects("Courses", 200)

#         # Deduplicate by course_id (multiple lessons per course)
#         seen = {}
#         for c in raw:
#             cid = str(getattr(c, "course_id", ""))
#             if cid not in seen:
#                 seen[cid] = c

#         courses = [flatten_osdk_object(c) for c in seen.values()]

#         # Apply filters
#         if category:
#             courses = [c for c in courses if str(c.get("tag", "")).lower() == category.lower()]
#         if level:
#             courses = [c for c in courses if str(c.get("level", "")).lower() == level.lower()]

#         total = len(courses)
#         paginated = courses[offset:offset + limit]

#         formatted = []
#         for c in paginated:
#             formatted.append({
#                 "id": str(c.get("course_id", c.get("id", ""))),
#                 "title": c.get("title") or c.get("course_name1", "Untitled"),
#                 "tag": c.get("tag", "General"),
#                 "duration": c.get("duration") or c.get("duration1", "Self-paced"),
#                 "instructor": c.get("instructor", "ItsYar Team"),
#                 "description": c.get("description", ""),
#                 "image": f"/api/courses/thumbnail/{c.get('course_id', c.get('id', ''))}",
#                 "badge": c.get("badge"),
#                 "level": c.get("level", "Beginner"),
#             })

#         return {"courses": formatted, "total": total, "offset": offset, "limit": limit}

#     except Exception as e:
#         print(f"[FOUNDRY ERROR] Courses fetch failed: {str(e)}")
#         return {"courses": [], "total": 0, "offset": offset, "limit": limit}




def search_courses_catalog(query_str: str, limit: int = 10) -> Dict[str, Any]:
    """Search courses by keyword (deduplicated)."""
    if not is_foundry_configured():
        return {"results": [], "query": query_str, "count": 0}

    try:
        raw = _take_objects("Courses", 200)

        # Deduplicate by course_id
        seen = {}
        for c in raw:
            cid = str(getattr(c, "course_id", ""))
            if cid not in seen:
                seen[cid] = c
        courses = [flatten_osdk_object(c) for c in seen.values()]

        q = query_str.lower()
        results = [
            c for c in courses
            if q in str(c.get("course_name1", "")).lower()
            or q in str(c.get("name", "")).lower()
            or q in str(c.get("title", "")).lower()
            or q in str(c.get("description", "")).lower()
            or q in str(c.get("tag", "")).lower()
        ]

        formatted = []
        for c in results[:limit]:
            formatted.append({
                "id": str(c.get("course_id", c.get("id", ""))),
                "title": c.get("title") or c.get("course_name1", "Untitled"),
                "tag": c.get("tag", "General"),
                "duration": c.get("duration") or c.get("duration1", "Self-paced"),
                "instructor": c.get("instructor", "ItsYar Team"),
                "description": c.get("description", ""),
                "image": f"/api/courses/thumbnail/{c.get('course_id', c.get('id', ''))}",
                "badge": c.get("badge"),
                "level": c.get("level", "Beginner"),
            })

        return {"results": formatted, "query": query_str, "count": len(formatted)}

    except Exception as e:
        print(f"[FOUNDRY ERROR] Course search failed: {str(e)}")
        return {"results": [], "query": query_str, "count": 0}


####################################################################################################################333

# ═══════════════════════════════════════════════════════════════
# COURSES — VIDEO FROM FOUNDRY MEDIA
# ═══════════════════════════════════════════════════════════════
# ## Single module
# def get_course_video_content(course_id: str) -> tuple:
#     """Fetch video content from Foundry using OSDK media property."""
#     if not is_foundry_configured():
#         return (None, None)

#     try:
#         try:
#             pk_value = int(course_id)
#         except ValueError:
#             pk_value = course_id

#         with AllowBetaFeatures():
#             client = foundry_osdk.get_client()
#             course_obj = client.ontology.objects.Courses.get(pk_value)

#             # Read video from the 'video' media property
#             media_stream = course_obj.video.get_media_content()
#             content = media_stream.read()

#         return (content, "video/mp4")

#     except Exception as e:
#         print(f"[FOUNDRY ERROR] Video content fetch failed: {str(e)}")
#         return (None, None)

# for multiple courses
def get_course_video_content(course_id: str, module_id: str = None) -> tuple:
    """Fetch video for a specific module (lesson) from Foundry. Returns (stream, content_type, size)."""
    if not is_foundry_configured():
        return (None, None, None)

    try:
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            all_courses = client.ontology.objects.Courses.take(200)

            if module_id:
                target = next(
                    (c for c in all_courses
                     if str(getattr(c, "course_id", "")) == str(course_id)
                     and str(getattr(c, "lesson_id", "")) == str(module_id)),
                    None
                )
            else:
                course_items = [c for c in all_courses if str(getattr(c, "course_id", "")) == str(course_id)]
                course_items.sort(key=lambda c: getattr(c, "lesson_id", 0))
                target = course_items[0] if course_items else None

            if not target:
                return (None, None, None)

            metadata = target.video.get_media_metadata()
            size_bytes = metadata.size_bytes if metadata else None

            media_stream = target.video.get_media_content()

        return (media_stream, "video/mp4", size_bytes)

    except Exception as e:
        print(f"[FOUNDRY ERROR] Video content fetch failed: {str(e)}")
        return (None, None, None)


def get_valid_course_ids() -> set:
    """Get set of valid course IDs from the Courses object."""
    if not is_foundry_configured():
        return set()

    try:
        raw = _take_objects("Courses", 200)
        return {str(getattr(c, "course_id", "")) for c in raw}
    except Exception:
        return set()


########################################################################################################################

# ═══════════════════════════════════════════════════════════════
# COURSES — LOOK (COMBINED LIST + SEARCH)
# ═══════════════════════════════════════════════════════════════

def look_courses(
    query: Optional[str] = None,
    offset: int = 0,
    limit: int = 6,
    category: Optional[str] = None,
    level: Optional[str] = None
) -> Dict[str, Any]:
    """
    Combined listing + search endpoint.
    - No query → returns all courses (paginated, filterable)
    - With query → searches by title/name + applies filters
    """
    if not is_foundry_configured():
        return {"courses": [], "total": 0, "offset": offset, "limit": limit, "query": query}

    try:
        raw = _take_objects("Courses", 200)
        courses = [flatten_osdk_object(c) for c in raw]

        # Apply keyword search if query provided
        if query:
            q = query.lower()
            courses = [
                c for c in courses
                if q in str(c.get("course_name1", "")).lower()
                or q in str(c.get("name", "")).lower()
                or q in str(c.get("title", "")).lower()
                or q in str(c.get("description", "")).lower()
                or q in str(c.get("tag", "")).lower()
            ]

        # Apply category filter
        if category:
            courses = [c for c in courses if str(c.get("tag", "")).lower() == category.lower()]

        # Apply level filter
        if level:
            courses = [c for c in courses if str(c.get("level", "")).lower() == level.lower()]

        # Calculate total before pagination
        total = len(courses)

        # Apply pagination
        paginated = courses[offset:offset + limit]

        # Format each course for response
        formatted = []
        for c in paginated:
            formatted.append({
                "id": str(c.get("course_id", c.get("id", ""))),
                "title": c.get("title") or c.get("course_name1", "Untitled"),
                "tag": c.get("tag", "General"),
                "duration": c.get("duration") or c.get("duration1", "Self-paced"),
                "instructor": c.get("instructor", "ItsYar Team"),
                "description": c.get("description", ""),
                "image": c.get("image", ""),
                "badge": c.get("badge"),
                "level": c.get("level", "Beginner"),
            })

        return {
            "courses": formatted,
            "total": total,
            "offset": offset,
            "limit": limit,
            "query": query,
        }

    except Exception as e:
        print(f"[FOUNDRY ERROR] Look courses failed: {str(e)}")
        return {"courses": [], "total": 0, "offset": offset, "limit": limit, "query": query}


# ═══════════════════════════════════════════════════════════════
# COURSES — MODULES
# ═══════════════════════════════════════════════════════════════
# def get_single_course(course_id: str) -> Optional[Dict[str, Any]]:
#         if not is_foundry_configured():
#             return None

#         try:
#             try:
#                 pk_value = int(course_id)
#             except ValueError:
#                 pk_value = course_id

#             with AllowBetaFeatures():
#                 client = foundry_osdk.get_client()
#                 if not hasattr(client.ontology.objects, "Courses"):
#                     return None

#                 try:
#                     raw = client.ontology.objects.Courses.get(pk_value)
#                     return flatten_osdk_object(raw)
#                 except Exception:
#                     pass

#                 if Courses is not None:
#                     for pk_name in ["course_id", "id", "courseId"]:
#                         if hasattr(Courses.object_type, pk_name):
#                             prop = getattr(Courses.object_type, pk_name)
#                             results = client.ontology.objects.Courses.where(prop == pk_value).take(1)
#                             if results:
#                                 return flatten_osdk_object(results[0])
#             return None
#         except Exception as e:
#             print(f"[FOUNDRY ERROR] Single course fetch failed: {str(e)}")
#             return None

#For multiple courses
def get_single_course(course_id: str) -> Optional[Dict[str, Any]]:
    """Get course info (first lesson record, for course-level data)."""
    if not is_foundry_configured():
        return None

    try:
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            if not hasattr(client.ontology.objects, "Courses"):
                return None

            all_courses = client.ontology.objects.Courses.take(200)
            # Get first record for this course (for course-level info)
            target = next(
                (c for c in all_courses if str(getattr(c, "course_id", "")) == str(course_id)),
                None
            )

            if not target:
                return None

            return flatten_osdk_object(target)

    except Exception as e:
        print(f"[FOUNDRY ERROR] Single course fetch failed: {str(e)}")
        return None

# ═══════════════════════════════════════════════════════════════
# COURSES — MODULES (FROM CURRICULUM OBJECT)
# ═══════════════════════════════════════════════════════════════

# def get_course_modules(course_id: str) -> Dict[str, Any]:
#     """
#     Get full course curriculum from Curriculum objects in Foundry.
#     Falls back to single-module (from Course itself) if no Curriculum items found.
#     """
#     if not is_foundry_configured():
#         return {"course": {"id": course_id, "title": "", "description": "", "curriculum": []}}

#     try:
#         course = get_single_course(course_id=course_id)
#         if not course:
#             return {"course": {"id": course_id, "title": "", "description": "", "curriculum": []}}

#         # Fetch Curriculum items for this course
#         curriculum_items = _get_curriculum_for_course(course_id)

#         if curriculum_items:
#             # Build curriculum from Curriculum objects
#             curriculum = []
#             for item in curriculum_items:
#                 # Build materials for this module
#                 materials = []
#                 if course.get("derived") or course.get("course_resources1"):
#                     materials.append({
#                         "id": f"m-{course_id}-pdf",
#                         "title": "Course PDF Notes",
#                         "type": "pdf",
#                         "meta": "PDF Document",
#                         "url": f"/api/courses/{course_id}/pdf",
#                         "pdf_status": "success",
#                     })

#                 # Check if quiz exists for this course
#                 has_quiz = False
#                 try:
#                     raw_quizzes = _take_objects("Quizes", 200)
#                     course_questions = [q for q in raw_quizzes if str(getattr(q, "course_id", "")) == str(course_id)]
#                     has_quiz = len(course_questions) > 0
#                 except Exception:
#                     pass

#                 module = {
#                     "id": item.get("id"),
#                     "title": item.get("title", "Untitled Module"),
#                     "duration": item.get("duration", "Self-paced"),
#                     "items": item.get("items"),  
#                     "has_quiz": has_quiz,
#                     "video_url": f"/api/courses/video/{course_id}",
#                     "summary": course.get("about_the_course") or course.get("description", ""),
#                     "materials": materials,
#                     "course_id": str(course_id),
#                     "module_id": str(item.get("curriculum_id", course_id)),
#                 }
#                 curriculum.append(module)
#         else:
#             # Fallback: single module from Course itself
#             materials = []
#             if course.get("derived") or course.get("course_resources1"):
#                 materials.append({
#                     "id": f"m-{course_id}-pdf",
#                     "title": "Course PDF Notes",
#                     "type": "pdf",
#                     "meta": "PDF Document",
#                     "url": f"/api/courses/{course_id}/pdf",
#                     "pdf_status": "success",
#                 })

#             has_quiz = False
#             try:
#                 raw_quizzes = _take_objects("Quizes", 200)
#                 course_questions = [q for q in raw_quizzes if str(getattr(q, "course_id", "")) == str(course_id)]
#                 has_quiz = len(course_questions) > 0
#             except Exception:
#                 pass

#             curriculum = [{
#                 "id": int(course_id) if course_id.isdigit() else course_id,
#                 "title": course.get("title") or course.get("course_name1", "Module 1"),
#                 "duration": course.get("duration1") or "Self-paced",
#                 "items": None,
#                 "has_quiz": has_quiz,
#                 "video_url": f"/api/courses/video/{course_id}",
#                 "summary": course.get("about_the_course") or course.get("description", ""),
#                 "materials": materials,
#                 "course_id": str(course_id),
#                 "module_id": str(course_id),
#             }]

#         return {
#             "course": {
#                 "id": str(course.get("course_id", course_id)),
#                 "title": course.get("title") or course.get("course_name1", ""),
#                 "description": course.get("description") or course.get("about_the_course", ""),
#                 "modules_count": len(curriculum),
#                 "curriculum": curriculum,
#             }
#         }

#     except Exception as e:
#         print(f"[FOUNDRY ERROR] Get course modules failed: {str(e)}")
#         return {"course": {"id": course_id, "title": "", "description": "", "curriculum": []}}


# #single course
# def get_course_modules(course_id: str) -> Dict[str, Any]:
#     """
#     Get full course curriculum from Curriculum objects in Foundry.
#     Falls back to single-module (from Course itself) if no Curriculum items found.
#     """
#     if not is_foundry_configured():
#         return {"course": {"id": course_id, "title": "", "description": "", "modules_count": 0, "curriculum": []}}

#     try:
#         course = get_single_course(course_id=course_id)
#         if not course:
#             return {"course": {"id": course_id, "title": "", "description": "", "modules_count": 0, "curriculum": []}}

#         # Fetch Curriculum items for this course
#         curriculum_items = _get_curriculum_for_course(course_id)

#         # Check if quiz exists for this course (once, not per module)
#         has_quiz = False
#         try:
#             raw_quizzes = _take_objects("Quizes", 200)
#             course_questions = [q for q in raw_quizzes if str(getattr(q, "course_id", "")) == str(course_id)]
#             has_quiz = len(course_questions) > 0
#         except Exception:
#             pass

#         # # Build materials (shared)
#         # materials = []
#         # if course.get("derived") or course.get("course_resources1"):
#         #     materials.append({
#         #         "id": f"m-{course_id}-pdf",
#         #         "title": "Course PDF Notes",
#         #         "type": "pdf",
#         #         "meta": "PDF Document",
#         #         "url": f"/api/courses/{course_id}/pdf",
#         #         "pdf_status": "success",
#         #     })
#         # Build materials — PDF always available (served from OSDK media)
#         materials = [{
#             "id": f"m-{course_id}-pdf",
#             "title": "Course PDF Notes",
#             "type": "pdf",
#             "meta": "PDF Document",
#             "url": f"/api/courses/{course_id}/pdf",
#             "pdf_status": "success",
#         }]

#         if curriculum_items:
#             curriculum = []
#             for item in curriculum_items:
#                 # Build lesson inside the module
#                 lesson = {
#                     "id": str(course_id),
#                     "has_quiz": has_quiz,
#                     "title": item.get("title", "Untitled Lesson"),
#                     "video_url": f"/api/courses/video/{course_id}",
#                     "summary": course.get("about_the_course") or course.get("description", ""),
#                     "materials": materials,
#                 }

#                 module = {
#                     "id": item.get("id"),
#                     "title": item.get("title", "Untitled Module"),
#                     "duration": item.get("duration", "Self-paced"),
#                     "items": item.get("items"),
#                     "course_id": str(course_id),
#                     "module_id": str(item.get("id", course_id)),
#                     "lessons": [lesson],
#                 }
#                 curriculum.append(module)
#         else:
#             # Fallback: single module from Course itself
#             lesson = {
#                 "id": str(course_id),
#                 "has_quiz": has_quiz,
#                 "title": course.get("title") or course.get("course_name1", "Lesson 1"),
#                 "video_url": f"/api/courses/video/{course_id}",
#                 "summary": course.get("about_the_course") or course.get("description", ""),
#                 "materials": materials,
#             }

#             curriculum = [{
#                 "id": int(course_id) if course_id.isdigit() else course_id,
#                 "title": course.get("title") or course.get("course_name1", "Module 1"),
#                 "duration": course.get("duration1") or "Self-paced",
#                 "items": None,
#                 "course_id": str(course_id),
#                 "module_id": str(course_id),
#                 "lessons": [lesson],
#             }]

#         return {
#             "course": {
#                 "id": str(course.get("course_id", course_id)),
#                 "title": course.get("title") or course.get("course_name1", ""),
#                 "description": course.get("description") or course.get("about_the_course", ""),
#                 "modules_count": len(curriculum),
#                 "curriculum": curriculum,
#             }
#         }

#     except Exception as e:
#         print(f"[FOUNDRY ERROR] Get course modules failed: {str(e)}")
#         return {"course": {"id": course_id, "title": "", "description": "", "modules_count": 0, "curriculum": []}}

# for multiple courses
def get_course_modules(course_id: str) -> Dict[str, Any]:
    """Get course curriculum with all modules (lessons) from Foundry."""
    if not is_foundry_configured():
        return {"course": {"id": course_id, "title": "", "description": "", "modules_count": 0, "curriculum": []}}

    try:
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            all_courses = client.ontology.objects.Courses.take(200)

            # Get all lessons for this course
            course_lessons = [
                c for c in all_courses
                if str(getattr(c, "course_id", "")) == str(course_id)
            ]
            course_lessons.sort(key=lambda c: getattr(c, "lesson_id", 0))

        if not course_lessons:
            return {"course": {"id": course_id, "title": "", "description": "", "modules_count": 0, "curriculum": []}}

        # Course-level info from first lesson
        first = course_lessons[0]
        course_title = getattr(first, "course_name1", "") or ""
        course_desc = getattr(first, "description", "") or getattr(first, "about_the_course", "") or ""

        # Check quiz
        has_quiz = False
        try:
            raw_quizzes = _take_objects("Quizes", 200)
            course_questions = [q for q in raw_quizzes if str(getattr(q, "course_id", "")) == str(course_id)]
            has_quiz = len(course_questions) > 0
        except Exception:
            pass

        # Build modules (each Foundry lesson = one module in our API)
        modules = []
        for c in course_lessons:
            mid = str(getattr(c, "lesson_id", ""))
            modules.append({
                "id": mid,
                "module_id": mid,
                "course_id": str(course_id),
                "title": getattr(c, "lesson_title", None) or "Untitled Module", #title of the module
                "summary": getattr(c, "summary1", None) or getattr(c, "about_the_course", "") or "", #summary of the module
                "has_quiz": has_quiz,
                "video_url": f"/api/courses/video/{course_id}/{mid}",
                "pdf_url": f"/api/courses/{course_id}/pdf/{mid}",
                "materials": [{
                    "id": f"m-{course_id}-{mid}-pdf",
                    "title": "Module PDF Notes",
                    "type": "pdf",
                    "url": f"/api/courses/{course_id}/pdf/{mid}",
                    "pdf_status": "success",
                }],
            })

        # Build as single curriculum entry with multiple modules
        curriculum = [{
            "id": 1,
            "title": course_title,
            "duration": getattr(first, "duration1", "Self-paced"),
            "course_id": str(course_id),
            "lessons": modules,
        }]

        return {
            "course": {
                "id": str(course_id),
                "title": course_title,
                "description": course_desc,
                "modules_count": len(modules),
                "curriculum": curriculum,
            }
        }

    except Exception as e:
        print(f"[FOUNDRY ERROR] Get course modules failed: {str(e)}")
        return {"course": {"id": course_id, "title": "", "description": "", "modules_count": 0, "curriculum": []}}
 

## before multiple modules
# def _get_curriculum_for_course(course_id: str) -> List[Dict[str, Any]]:
#     """Fetch Curriculum objects for a specific course."""
#     try:
#         with AllowBetaFeatures():
#             client = foundry_osdk.get_client()
#             if not hasattr(client.ontology.objects, "Curriculum"):
#                 return []

#             all_items = client.ontology.objects.Curriculum.take(100)

#             # Filter by course_id (include unlinked items as temp fix)
#             course_items = [
#                 item for item in all_items
#                 if str(getattr(item, "course_id", "") or "") == str(course_id)
#                 or getattr(item, "course_id", None) is None  # Temp: include unlinked items
#             ]
#             course_items.sort(key=lambda x: getattr(x, "curriculum_id", 0))

#             # Return clean data
#             cleaned = []
#             for item in course_items:
#                 cleaned.append({
#                     "id": getattr(item, "curriculum_id", None),
#                     "course_id": str(course_id),
#                     "title": getattr(item, "title1", None) or "Untitled Module",
#                     "duration": getattr(item, "duration1", None) or "Self-paced",
#                     "items": getattr(item, "items1", None),
#                 })
#             return cleaned

#     except Exception as e:
#         print(f"[FOUNDRY ERROR] Curriculum fetch failed: {str(e)}")
#         return []

### after multiple modules
def _get_curriculum_for_course(course_id: str) -> List[Dict[str, Any]]:
    """Build curriculum from Courses object lessons (reliable duration)."""
    try:
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            all_courses = client.ontology.objects.Courses.take(200)

            course_lessons = [
                c for c in all_courses
                if str(getattr(c, "course_id", "")) == str(course_id)
            ]
            course_lessons.sort(key=lambda c: getattr(c, "lesson_id", 0))

            cleaned = []
            for item in course_lessons:
                cleaned.append({
                    "id": getattr(item, "lesson_id", None),
                    "module_id": str(getattr(item, "lesson_id", "")),
                    "course_id": str(course_id),
                    "title": getattr(item, "lesson_title", None) or "Untitled Module",
                    "duration": getattr(item, "duration1", None) or "Self-paced",
                    "summary": getattr(item, "summary1", None) or "",
                    "items": None,
                })
            return cleaned

    except Exception as e:
        print(f"[FOUNDRY ERROR] Curriculum fetch failed: {str(e)}")
        return []


# # Single Course
# def get_module_content(course_id: str, module_id: str) -> Optional[Dict[str, Any]]:
#     """Get module content — video proxy URL and PDF resource."""
#     if not is_foundry_configured():
#         return None

#     try:
#         course = get_single_course(course_id=course_id)
#         if not course:
#             return None

#         # Build the proxy video URL
#         raw_video_url = course.get("course_url1") or ""
#         video_url = f"/api/courses/video/{course_id}"

#         return {
#             "courseId": course_id,
#             "moduleId": module_id,
#             "title": course.get("title") or course.get("course_name1"),
#             "video_url": f"/api/courses/video/{course_id}",
#             "pdf_resource": f"/api/courses/{course_id}/pdf",
#             "content_id": course.get("content_id"),
#         }


#     except Exception as e:
#         print(f"[FOUNDRY ERROR] Get module content failed: {str(e)}")
#         return None

## Multiple Courses
def get_module_content(course_id: str, module_id: str) -> Optional[Dict[str, Any]]:
    """Get content for a specific module."""
    if not is_foundry_configured():
        return None

    try:
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            all_courses = client.ontology.objects.Courses.take(200)

            target = next(
                (c for c in all_courses
                 if str(getattr(c, "course_id", "")) == str(course_id)
                 and str(getattr(c, "lesson_id", "")) == str(module_id)),
                None
            )

            if not target:
                return None

            return {
                "course_id": str(course_id),
                "module_id": str(module_id),
                "title": getattr(target, "lesson_title", None) or "Untitled",
                "video_url": f"/api/courses/video/{course_id}/{module_id}",
                "pdf_url": f"/api/courses/{course_id}/pdf/{module_id}",
                "materials": [{
                    "id": f"m-{course_id}-{module_id}-pdf",
                    "title": "Module PDF Notes",
                    "type": "pdf",
                    "url": f"/api/courses/{course_id}/pdf/{module_id}",
                    "pdf_status": "success",
                }],
            }

    except Exception as e:
        print(f"[FOUNDRY ERROR] Get module content failed: {str(e)}")
        return None


# # Single module
# def get_course_pdf_content(course_id: str) -> tuple:
#     """Fetch PDF content from Foundry using OSDK media property."""
#     if not is_foundry_configured():
#         return (None, None)

#     try:
#         try:
#             pk_value = int(course_id)
#         except ValueError:
#             pk_value = course_id

#         with AllowBetaFeatures():
#             client = foundry_osdk.get_client()
#             course_obj = client.ontology.objects.Courses.get(pk_value)
#             media_stream = course_obj.course_resources1.get_media_content()
            
#             # get_media_content() returns BytesIO — read the bytes from it
#             content = media_stream.read()

#         return (content, "application/pdf")

#     except Exception as e:
#         print(f"[FOUNDRY ERROR] PDF content fetch failed: {str(e)}")
#         return (None, None)

##for multiple courses
def get_course_pdf_content(course_id: str, module_id: str = None) -> tuple:
    """Fetch PDF for a specific module (lesson) from Foundry."""
    if not is_foundry_configured():
        return (None, None)

    try:
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            all_courses = client.ontology.objects.Courses.take(200)

            # Find the specific module (lesson_id in Foundry = module_id in our API)
            if module_id:
                target = next(
                    (c for c in all_courses
                     if str(getattr(c, "course_id", "")) == str(course_id)
                     and str(getattr(c, "lesson_id", "")) == str(module_id)),
                    None
                )
            else:
                course_items = [c for c in all_courses if str(getattr(c, "course_id", "")) == str(course_id)]
                course_items.sort(key=lambda c: getattr(c, "lesson_id", 0))
                target = course_items[0] if course_items else None

            if not target:
                return (None, None)

            media_stream = target.course_resources1.get_media_content()
            content = media_stream.read()

        return (content, "application/pdf")

    except Exception as e:
        print(f"[FOUNDRY ERROR] PDF content fetch failed: {str(e)}")
        return (None, None)



# ═══════════════════════════════════════════════════════════════
# COURSES — ENROLLMENT
# ═══════════════════════════════════════════════════════════════

def get_user_enrolled_courses(user_id: str) -> Dict[str, Any]:
    if not is_foundry_configured():
        return {"courses": [], "count": 0}

    try:
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            if not hasattr(client.ontology.objects, "VanyarEnrolment"):
                return {"courses": [], "count": 0}

            if VanyarEnrolment is not None and hasattr(VanyarEnrolment.object_type, "user_id"):
                prop = getattr(VanyarEnrolment.object_type, "user_id")
                enrollments = client.ontology.objects.VanyarEnrolment.where(prop == user_id).take(50)
            else:
                all_enrolments = client.ontology.objects.VanyarEnrolment.take(200)
                enrollments = [e for e in all_enrolments if getattr(e, "user_id", None) == user_id]

        enrolled_courses = [flatten_osdk_object(e) for e in enrollments]
        return {"courses": enrolled_courses, "count": len(enrolled_courses)}

    except Exception as e:
        print(f"[FOUNDRY ERROR] User enrolled courses failed: {str(e)}")
        return {"courses": [], "count": 0}


def check_user_enrollment(course_id: str, user_id: str) -> Dict[str, Any]:
    """Check if user is enrolled. event_id = course_id in VanyarEnrolment."""
    if not is_foundry_configured():
        return {"isEnrolled": False, "courseId": course_id}

    try:
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            if not hasattr(client.ontology.objects, "VanyarEnrolment"):
                return {"isEnrolled": False, "courseId": course_id}

            all_enrolments = client.ontology.objects.VanyarEnrolment.take(200)

            # event_id IS the course_id in enrollment records
            match = [
                e for e in all_enrolments
                if str(getattr(e, "user_id", "")) == str(user_id)
                and str(getattr(e, "event_id", "")) == str(course_id)
            ]
        return {"isEnrolled": len(match) > 0, "courseId": course_id}

    except Exception as e:
        print(f"[FOUNDRY ERROR] Enrollment check failed: {str(e)}")
        return {"isEnrolled": False, "courseId": course_id}


def execute_course_enrollment_action(course_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Enroll user in a course by calling create_enrolment action.
    Params: user_id, status="in progress", eventid=course_id, enrollment_id=UUID
    """
    import uuid

    if not is_foundry_configured():
        enrollment_id = str(uuid.uuid4())
        return {"status": "success", "message": "Enrolled (mock)", "courseId": course_id, "enrollment_id": enrollment_id}

    try:
        import inspect
        enrollment_id = str(uuid.uuid4())

        with AllowBetaFeatures():
            client = foundry_osdk.get_client()

            if not hasattr(client.ontology.actions, "create_enrolment"):
                return {"status": "error", "message": "create_enrolment action not available in SDK"}

            sig = inspect.signature(client.ontology.actions.create_enrolment)
            expected = list(sig.parameters.keys())
            print(f"[DEBUG] create_enrolment expects: {expected}")

            try:
                course_id_val = int(course_id)
            except ValueError:
                course_id_val = course_id

            param_values = {
                "user_id": user_id, "userId": user_id, "user": user_id,
                "status": "in progress", "Status": "in progress",
                "event_id": str(course_id_val), "eventId": str(course_id_val), "eventid": str(course_id_val),
                "event": str(course_id_val), "course_id": str(course_id_val), "courseId": str(course_id_val),
                "enrollment_id": enrollment_id, "enrolment_id": enrollment_id,
                "enrollmentId": enrollment_id, "enrolmentId": enrollment_id,
            }

            kwargs = {p: param_values[p] for p in expected if p in param_values}
            print(f"[DEBUG] Calling create_enrolment with: {kwargs}")
            client.ontology.actions.create_enrolment(**kwargs)

        return {
            "status": "success",
            "message": f"Enrolled in course {course_id}",
            "courseId": course_id,
            "enrollment_id": enrollment_id
        }

    except Exception as e:
        print(f"[FOUNDRY ERROR] Course enrollment failed: {str(e)}")
        return {"status": "error", "message": f"Enrollment failed: {str(e)}"}

# ═══════════════════════════════════════════════════════════════
# COURSES — MARK COMPLETE
# ═══════════════════════════════════════════════════════════════

def mark_course_complete(course_id: str, user_id: str) -> Dict[str, Any]:
    """
    Mark a course as complete by calling mark_complete action.
    Finds enrollment_id first, then calls the action.
    """
    if not is_foundry_configured():
        return {"status": "success", "message": "Course marked complete (mock)"}

    try:
        import inspect

        with AllowBetaFeatures():
            client = foundry_osdk.get_client()

            if not hasattr(client.ontology.objects, "VanyarEnrolment"):
                return {"status": "error", "message": "VanyarEnrolment not available"}

            try:
                course_id_val = int(course_id)
            except ValueError:
                course_id_val = course_id

            # Find enrollment for this user + course
            all_enrolments = client.ontology.objects.VanyarEnrolment.take(200)
            match = [
                e for e in all_enrolments
                if str(getattr(e, "user_id", "")) == str(user_id)
                and str(getattr(e, "event_id", "")) == str(course_id)
            ]

            if not match:
                return {"status": "error", "message": "No enrollment found for this user and course"}

            enrolment_id = getattr(match[0], "enrolment_id", None)
            if not enrolment_id:
                return {"status": "error", "message": "Enrollment record has no enrolment_id"}

            # Call mark_complete action
            if not hasattr(client.ontology.actions, "mark_complete"):
                return {"status": "error", "message": "mark_complete action not available in SDK"}

            sig = inspect.signature(client.ontology.actions.mark_complete)
            expected = list(sig.parameters.keys())
            print(f"[DEBUG] mark_complete expects: {expected}")

            param_values = {
                "enrolment_id": enrolment_id, "enrollment_id": enrolment_id,
                "enrolmentId": enrolment_id, "enrollmentId": enrolment_id,
                "enrolment": enrolment_id, "vanyar_enrolment": enrolment_id,
                "status": "completed", "Status": "completed",
                "event_id": str(course_id), "eventId": str(course_id), "eventid": str(course_id),
                "event": str(course_id), "course_id": str(course_id), "courseId": str(course_id),
            }


            kwargs = {p: param_values[p] for p in expected if p in param_values}
            print(f"[DEBUG] Calling mark_complete with: {kwargs}")
            client.ontology.actions.mark_complete(**kwargs)

        return {"status": "success", "message": f"Course {course_id} marked as completed"}

    except Exception as e:
        print(f"[FOUNDRY ERROR] Mark complete failed: {str(e)}")
        return {"status": "error", "message": f"Mark complete failed: {str(e)}"}

# ═══════════════════════════════════════════════════════════════
# COURSES — QUIZ + AUTO-COMPLETE
# ═══════════════════════════════════════════════════════════════

# # Single Course
# def get_course_quiz(course_id: str, module_id: str = None) -> Dict[str, Any]:
#     """Fetch quiz questions for a course from Quizes object. Returns structured quiz format."""
#     empty_quiz = {
#         "quiz": {
#             "id": f"quiz_{course_id}",
#             "title": "Module Test",
#             "path": "",
#             "time_limit": 10,
#             "questions": [],
#         }
#     }

#     if not is_foundry_configured():
#         return empty_quiz

#     try:
#         # Get course info for title/path
#         course = get_single_course(course_id=course_id)
#         course_title = ""
#         if course:
#             course_title = course.get("title") or course.get("course_name1", "")

#         # Fetch quiz questions from Foundry
#         raw = _take_objects("Quizes", 200)

#         course_questions = [
#             q for q in raw
#             if str(getattr(q, "course_id", "")) == str(course_id)
#         ]

#         # Build questions array
#         questions = []
#         for idx, q in enumerate(course_questions):
#             flat = flatten_osdk_object(q)

#             # Get options as a list of strings
#             options_raw = flat.get("multiple_choice", [])
#             if isinstance(options_raw, str):
#                 import json
#                 try:
#                     options_raw = json.loads(options_raw)
#                 except (json.JSONDecodeError, ValueError):
#                     options_raw = [options_raw]

#             if not isinstance(options_raw, list):
#                 options_raw = []

#             # Determine correct answer as letter (a, b, c, d)
#             answer_raw = flat.get("answer", [])
#             if isinstance(answer_raw, str):
#                 answer_raw = [answer_raw.strip()]
#             elif not isinstance(answer_raw, list):
#                 answer_raw = [str(answer_raw)]

#             # Convert to lowercase letter
#             correct_letter = "a"
#             if answer_raw:
#                 correct_val = answer_raw[0].strip().upper()
#                 # If already a letter (A, B, C, D)
#                 if correct_val in ("A", "B", "C", "D", "E"):
#                     correct_letter = correct_val.lower()
#                 # If it's a number (1, 2, 3, 4) → convert to letter
#                 elif correct_val.isdigit():
#                     num = int(correct_val)
#                     letter_map = {1: "a", 2: "b", 3: "c", 4: "d", 5: "e"}
#                     correct_letter = letter_map.get(num, "a")
#                 # If it's index-based (0, 1, 2, 3)
#                 else:
#                     # Try matching answer text to options
#                     for i, opt in enumerate(options_raw):
#                         if str(opt).strip().lower() == correct_val.lower():
#                             index_map = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e"}
#                             correct_letter = index_map.get(i, "a")
#                             break

#             # Format question ID as q_001, q_002, etc.
#             question_id = f"q_{str(idx + 1).zfill(3)}"

#             questions.append({
#                 "id": question_id,
#                 "text": flat.get("question", ""),
#                 "options": options_raw,
#                 "correct_answer": correct_letter,
#             })

#         return {
#             "quiz": {
#                 "id": f"quiz_{course_id}_{module_id or '1'}",
#                 "title": f"Module Test: {course_title}",
#                 "path": course_title,
#                 "time_limit": 10,
#                 "questions": questions,
#             }
#         }

#     except Exception as e:
#         print(f"[FOUNDRY ERROR] Quiz fetch failed: {str(e)}")
#         return empty_quiz

## Multiple Course
def get_course_quiz(course_id: str, module_id: str = None) -> Dict[str, Any]:
    """Fetch quiz questions for a specific module."""
    empty_quiz = {
        "quiz": {
            "id": f"quiz_{course_id}_{module_id or '1'}",
            "title": "Module Test",
            "path": "",
            "time_limit": 10,
            "questions": [],
        }
    }

    if not is_foundry_configured():
        return empty_quiz

    try:
        # Get module-specific title
        quiz_title = ""
        if module_id:
            with AllowBetaFeatures():
                client = foundry_osdk.get_client()
                all_courses = client.ontology.objects.Courses.take(200)
                target = next(
                    (c for c in all_courses
                     if str(getattr(c, "course_id", "")) == str(course_id)
                     and str(getattr(c, "lesson_id", "")) == str(module_id)),
                    None
                )
                if target:
                    quiz_title = getattr(target, "lesson_title", "") or ""

        if not quiz_title:
            course = get_single_course(course_id=course_id)
            if course:
                quiz_title = course.get("title") or course.get("course_name1", "")

        # Fetch quiz questions
        raw = _take_objects("Quizes", 200)

        # Filter by course_id AND module_id
        course_questions = []
        for q in raw:
            q_course = str(getattr(q, "course_id", ""))
            q_module = str(getattr(q, "module_id", getattr(q, "lesson_id", "")))

            if q_course == str(course_id):
                if module_id and q_module and q_module != "None" and q_module != "":
                    # Quiz has module field — filter by it
                    if q_module == str(module_id):
                        course_questions.append(q)
                else:
                    # Quiz has no module field — include all for this course
                    course_questions.append(q)

        # Build questions
        questions = []
        for idx, q in enumerate(course_questions):
            flat = flatten_osdk_object(q)

            options_raw = flat.get("multiple_choice", [])
            if isinstance(options_raw, str):
                import json
                try:
                    options_raw = json.loads(options_raw)
                except (json.JSONDecodeError, ValueError):
                    options_raw = [options_raw]
            if not isinstance(options_raw, list):
                options_raw = []

            answer_raw = flat.get("answer", [])
            if isinstance(answer_raw, str):
                answer_raw = [answer_raw.strip()]
            elif not isinstance(answer_raw, list):
                answer_raw = [str(answer_raw)]

            correct_letter = "a"
            if answer_raw:
                correct_val = answer_raw[0].strip().upper()
                if correct_val in ("A", "B", "C", "D", "E"):
                    correct_letter = correct_val.lower()
                elif correct_val.isdigit():
                    num = int(correct_val)
                    letter_map = {1: "a", 2: "b", 3: "c", 4: "d", 5: "e"}
                    correct_letter = letter_map.get(num, "a")

            question_id = f"q_{str(idx + 1).zfill(3)}"
            questions.append({
                "id": question_id,
                "text": flat.get("question", ""),
                "options": options_raw,
                "correct_answer": correct_letter,
            })

        return {
            "quiz": {
                "id": f"quiz_{course_id}_{module_id or '1'}",
                "title": f"Module Test: {quiz_title}",
                "path": quiz_title,
                "time_limit": 10,
                "questions": questions,
            }
        }

    except Exception as e:
        print(f"[FOUNDRY ERROR] Quiz fetch failed: {str(e)}")
        return empty_quiz

# # Single course
# def grade_and_complete_course(course_id: str, user_id: str, submission_data: Any, module_id: str = None) -> Dict[str, Any]:
#     """
#     Grade quiz using Quizes object answer key.
#     If passed (>=70%), automatically mark course as complete.
#     Answer format: array (e.g., ["B"] or ["B", "D"])
#     """
#     PASSING_THRESHOLD = 70

#     if not is_foundry_configured():
#         return {"status": "success", "score": 0, "passed": False, "courseId": course_id, "total": 0, "correct": 0}

#     try:
#         # Step 1: Fetch quiz questions + answer key from Quizes object
#         raw = _take_objects("Quizes", 200)

#         course_questions = [
#             q for q in raw
#             if str(getattr(q, "course_id", "")) == str(course_id)
#         ]

#         if not course_questions:
#             # No quiz questions — auto-pass
#             complete_result = mark_course_complete(course_id=course_id, user_id=user_id)
#             return {
#                 "status": "success",
#                 "score": 100,
#                 "passed": True,
#                 "courseId": course_id,
#                 "moduleId": module_id,
#                 "total": 0,
#                 "correct": 0,
#                 "message": "No quiz available — course marked complete",
#                 "completion": complete_result
#             }

#         # Step 2: Build answer key using quize_primary_key → answer
#         answer_key = {}
#         for q in course_questions:
#             q_id = str(getattr(q, "quize_primary_key", ""))
#             correct = getattr(q, "answer", [])

#             if isinstance(correct, str):
#                 correct = [correct.strip()]
#             elif not isinstance(correct, list):
#                 correct = [str(correct)]

#             if q_id:
#                 answer_key[q_id] = [a.strip().lower() for a in correct]

#         # Step 3: Get student's submitted answers
#         if hasattr(submission_data, "answers"):
#             student_answers = submission_data.answers
#         elif isinstance(submission_data, dict):
#             student_answers = submission_data.get("answers", [])
#         else:
#             student_answers = []

#         # Step 4: Grade (array comparison)
#         total_questions = len(answer_key)
#         correct_count = 0

#         for submission in student_answers:
#             if hasattr(submission, "questionId"):
#                 q_id = str(submission.questionId)
#                 student_ans = submission.answer
#             elif isinstance(submission, dict):
#                 q_id = str(submission.get("questionId") or "")
#                 student_ans = submission.get("answer") or []
#             else:
#                 continue

#             if isinstance(student_ans, str):
#                 student_ans = [student_ans.strip()]
#             elif not isinstance(student_ans, list):
#                 student_ans = [str(student_ans)]

#             student_set = set(a.strip().lower() for a in student_ans)
#             correct_set = set(answer_key.get(q_id, []))

#             if student_set == correct_set:
#                 correct_count += 1

#         # Step 5: Calculate score
#         score_percent = round((correct_count / total_questions) * 100) if total_questions > 0 else 0
#         passed = score_percent >= PASSING_THRESHOLD

#         # Step 6: If passed → mark course complete
#         completion_result = None
#         if passed:
#             completion_result = mark_course_complete(course_id=course_id, user_id=user_id)

#         return {
#             "status": "success",
#             "score": score_percent,
#             "passed": passed,
#             "courseId": course_id,
#             "moduleId": module_id,
#             "total": total_questions,
#             "correct": correct_count,
#             "message": f"You scored {correct_count}/{total_questions} ({score_percent}%)" + (" — Course completed! 🎉" if passed else " — Try again"),
#             "completion": completion_result
#         }

#     except Exception as e:
#         print(f"[FOUNDRY ERROR] Quiz grading failed: {str(e)}")
#         return {
#             "status": "error",
#             "score": 0,
#             "passed": False,
#             "courseId": course_id,
#             "moduleId": module_id,
#             "total": 0,
#             "correct": 0,
#             "message": f"Grading failed: {str(e)}"
#         }

## multiple modules
def grade_and_complete_course(course_id: str, user_id: str, submission_data: Any, module_id: str = None) -> Dict[str, Any]:
    """
    Grade quiz using Quizes object answer key.
    If passed (>=70%), automatically mark course as complete.
    Answer format: array (e.g., ["B"] or ["B", "D"])
    """
    PASSING_THRESHOLD = 70

    if not is_foundry_configured():
        return {"status": "success", "score": 0, "passed": False, "courseId": course_id, "total": 0, "correct": 0}

    try:
        # Step 1: Fetch quiz questions + answer key from Quizes object
        raw = _take_objects("Quizes", 200)

        # Filter by course_id AND module_id
        course_questions = []
        for q in raw:
            q_course = str(getattr(q, "course_id", ""))
            q_module = str(getattr(q, "module_id", getattr(q, "lesson_id", "")))

            if q_course == str(course_id):
                if module_id and q_module and q_module != "None" and q_module != "":
                    if q_module == str(module_id):
                        course_questions.append(q)
                else:
                    # No module field on quiz — include all (legacy)
                    course_questions.append(q)


        if not course_questions:
            # No quiz questions — auto-pass
            complete_result = mark_course_complete(course_id=course_id, user_id=user_id)
            return {
                "status": "success",
                "score": 100,
                "passed": True,
                "courseId": course_id,
                "moduleId": module_id,
                "total": 0,
                "correct": 0,
                "message": "No quiz available — course marked complete",
                "completion": complete_result
            }

        # Step 2: Build answer key using quize_primary_key → answer
        answer_key = {}
        for q in course_questions:
            q_id = str(getattr(q, "quize_primary_key", ""))
            correct = getattr(q, "answer", [])

            if isinstance(correct, str):
                correct = [correct.strip()]
            elif not isinstance(correct, list):
                correct = [str(correct)]

            if q_id:
                answer_key[q_id] = [a.strip().lower() for a in correct]

        # Step 3: Get student's submitted answers
        if hasattr(submission_data, "answers"):
            student_answers = submission_data.answers
        elif isinstance(submission_data, dict):
            student_answers = submission_data.get("answers", [])
        else:
            student_answers = []

        # Step 4: Grade (array comparison)
        total_questions = len(answer_key)
        correct_count = 0

        for submission in student_answers:
            if hasattr(submission, "questionId"):
                q_id = str(submission.questionId)
                student_ans = submission.answer
            elif isinstance(submission, dict):
                q_id = str(submission.get("questionId") or "")
                student_ans = submission.get("answer") or []
            else:
                continue

            if isinstance(student_ans, str):
                student_ans = [student_ans.strip()]
            elif not isinstance(student_ans, list):
                student_ans = [str(student_ans)]

            student_set = set(a.strip().lower() for a in student_ans)
            correct_set = set(answer_key.get(q_id, []))

            if student_set == correct_set:
                correct_count += 1

        # Step 5: Calculate score
        score_percent = round((correct_count / total_questions) * 100) if total_questions > 0 else 0
        passed = score_percent >= PASSING_THRESHOLD

        # Step 6: If passed → mark course complete
        completion_result = None
        if passed:
            completion_result = mark_course_complete(course_id=course_id, user_id=user_id)

        return {
            "status": "success",
            "score": score_percent,
            "passed": passed,
            "courseId": course_id,
            "moduleId": module_id,
            "total": total_questions,
            "correct": correct_count,
            "message": f"You scored {correct_count}/{total_questions} ({score_percent}%)" + (" — Course completed! 🎉" if passed else " — Try again"),
            "completion": completion_result
        }

    except Exception as e:
        print(f"[FOUNDRY ERROR] Quiz grading failed: {str(e)}")
        return {
            "status": "error",
            "score": 0,
            "passed": False,
            "courseId": course_id,
            "moduleId": module_id,
            "total": 0,
            "correct": 0,
            "message": f"Grading failed: {str(e)}"
        }


# ═══════════════════════════════════════════════════════════════
# COURSES — CERTIFICATE
# ═══════════════════════════════════════════════════════════════

# def get_course_certificate_content(course_id: str) -> tuple:
#     """Fetch certificate image from Foundry using OSDK media property."""
#     if not is_foundry_configured():
#         return (None, None)

#     try:
#         try:
#             pk_value = int(course_id)
#         except ValueError:
#             pk_value = course_id

#         with AllowBetaFeatures():
#             client = foundry_osdk.get_client()
#             course_obj = client.ontology.objects.Courses.get(pk_value)
#             media_stream = course_obj.certificate.get_media_content()
#             content = media_stream.read()

#         return (content, "image/png")

#     except Exception as e:
#         print(f"[FOUNDRY ERROR] Certificate fetch failed: {str(e)}")
#         return (None, None)


#for multiple courses
def get_course_certificate_content(course_id: str) -> tuple:
    """Fetch certificate image from Foundry."""
    if not is_foundry_configured():
        return (None, None)

    try:
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            all_courses = client.ontology.objects.Courses.take(200)

            target = next(
                (c for c in all_courses if str(getattr(c, "course_id", "")) == str(course_id)),
                None
            )

            if not target:
                return (None, None)

            media_stream = target.certificate.get_media_content()
            content = media_stream.read()

        return (content, "image/png")

    except Exception as e:
        print(f"[FOUNDRY ERROR] Certificate fetch failed: {str(e)}")
        return (None, None)


## Complection check included
# def get_certificate_info(course_id: str, user_id: str, user_name: str) -> Optional[Dict[str, Any]]:
#     """Get certificate metadata — only if course is completed."""
#     if not is_foundry_configured():
#         return None

#     try:
#         # Check if course is completed
#         progress = get_course_progress(course_id=course_id, user_id=user_id)
#         if progress.get("status") != "completed":
#             return None

#         # Get course details
#         course = get_single_course(course_id=course_id)
#         if not course:
#             return None

#         # Generate certificate ID from course + user (deterministic)
#         cert_id = f"ITS-{course_id}-{user_id[:8].upper()}"

#         return {
#             "certificate_id": cert_id,
#             "course_title": course.get("title") or course.get("course_name1", ""),
#             "student_name": user_name,
#             "issue_date": progress.get("completed_at") or datetime.utcnow().strftime("%d %B %Y"),
#             "instructor_name": course.get("instructor", "ItsYar Team"),
#         }

#     except Exception as e:
#         print(f"[FOUNDRY ERROR] Certificate info failed: {str(e)}")
#         return None

def get_certificate_info(course_id: str, user_id: str, user_name: str) -> Optional[Dict[str, Any]]:
    """Get certificate metadata."""
    if not is_foundry_configured():
        return None

    try:
        # Get course details
        course = get_single_course(course_id=course_id)
        if not course:
            return None

        # Get enrollment info (for issue date)
        progress = get_course_progress(course_id=course_id, user_id=user_id)

        # Generate certificate ID
        cert_id = f"ITS-{course_id}-{user_id[:8].upper()}"

        return {
            "certificate_id": cert_id,
            "course_title": course.get("title") or course.get("course_name1", ""),
            "student_name": user_name,
            "issue_date": progress.get("completed_at") or datetime.utcnow().strftime("%d %B %Y"),
            "instructor_name": course.get("instructor", "ItsYar Team"),
        }

    except Exception as e:
        print(f"[FOUNDRY ERROR] Certificate info failed: {str(e)}")
        return None

# ═══════════════════════════════════════════════════════════════
# COURSES — PROGRESS (USING VANYAR PROGRESS)
# ═══════════════════════════════════════════════════════════════

def get_course_progress(course_id: str, user_id: str) -> Dict[str, Any]:
    """
    Get course progress using ProgressDetails (video tracking) + VanyarEnrolment (status).
    """
    if not is_foundry_configured():
        return {"courseId": course_id, "userId": user_id, "status": "not enrolled", "percentage": 0}

    try:
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()

            # Step 1: Check enrollment
            if not hasattr(client.ontology.objects, "VanyarEnrolment"):
                return {"courseId": course_id, "userId": user_id, "status": "not enrolled", "percentage": 0}

            all_enrolments = client.ontology.objects.VanyarEnrolment.take(200)
            match = [
                e for e in all_enrolments
                if str(getattr(e, "user_id", "")) == str(user_id)
                and str(getattr(e, "event_id", "")) == str(course_id)
            ]

            if not match:
                return {"courseId": course_id, "userId": user_id, "status": "not enrolled", "percentage": 0}

            enrollment = flatten_osdk_object(match[0])
            enrollment_status = enrollment.get("status", "in progress")

        # Step 2: Get video progress from ProgressDetails
        progress_data = get_progress_details_for_course(course_id, user_id)
        total_modules = progress_data.get("total_modules", 1)
        completed_modules = progress_data.get("completed_modules", 0)

        # Step 3: Calculate percentage
        if enrollment_status.upper() == "COMPLETED":
            percentage = 100
        else:
            percentage = progress_data.get("percentage", 0)

        # Step 4: Determine status
        if percentage == 100 or enrollment_status.upper() == "COMPLETED":
            status = "completed"
        elif percentage > 0 or enrollment_status.upper() in ("ACTIVE", "IN PROGRESS"):
            status = "in progress"
        else:
            status = enrollment_status

        return {
            "courseId": course_id,
            "userId": user_id,
            "status": status,
            "percentage": percentage,
            "total_modules": total_modules,
            "completed_modules": completed_modules,
            "enrollment_id": enrollment.get("enrolment_id"),
            "enrolled_at": enrollment.get("enrolled_at"),
            "completed_at": enrollment.get("completed_at"),
        }

    except Exception as e:
        print(f"[FOUNDRY ERROR] Course progress failed: {str(e)}")
        return {"courseId": course_id, "userId": user_id, "status": "unknown", "percentage": 0, "error": str(e)}



# # ═══════════════════════════════════════════════════════════════
# # COURSES — PROGRESS
# # ═══════════════════════════════════════════════════════════════

# def get_course_progress(course_id: str, user_id: str) -> Dict[str, Any]:
#     """Get enrollment status and completion for a course."""
#     if not is_foundry_configured():
#         return {"courseId": course_id, "userId": user_id, "status": "not enrolled"}

#     try:
#         with AllowBetaFeatures():
#             client = foundry_osdk.get_client()
#             if not hasattr(client.ontology.objects, "VanyarEnrolment"):
#                 return {"courseId": course_id, "userId": user_id, "status": "not enrolled"}

#             all_enrolments = client.ontology.objects.VanyarEnrolment.take(200)
#             match = [
#                 e for e in all_enrolments
#                 if str(getattr(e, "user_id", "")) == str(user_id)
#                 and str(getattr(e, "event_id", "")) == str(course_id)
#             ]

#         if not match:
#             return {"courseId": course_id, "userId": user_id, "status": "not enrolled"}

#         enrollment = flatten_osdk_object(match[0])
#         return {
#             "courseId": course_id,
#             "userId": user_id,
#             "status": enrollment.get("status", "in progress"),
#             "enrollment_id": enrollment.get("enrolment_id"),
#             "enrolled_at": enrollment.get("enrolled_at"),
#             "completed_at": enrollment.get("completed_at"),
#         }

#     except Exception as e:
#         print(f"[FOUNDRY ERROR] Course progress failed: {str(e)}")
#         return {"courseId": course_id, "userId": user_id, "status": "unknown", "error": str(e)}

# ═══════════════════════════════════════════════════════════════
# PROGRESS DETAILS (FOUNDRY — VIDEO WATCH TRACKING)
# ═══════════════════════════════════════════════════════════════

def update_progress_details(course_id: str, module_id: str, user_id: str, played_seconds: float, total_seconds: float, is_complete: bool) -> Dict[str, Any]:
    """Create or update video progress in Foundry ProgressDetails."""
    if not is_foundry_configured():
        return {"status": "error", "message": "Foundry not configured"}

    try:
        import inspect

        with AllowBetaFeatures():
            client = foundry_osdk.get_client()

            param_values_create = {
                "user_id1": str(user_id),
                "course_id1": int(course_id),
                "lesson_id": int(module_id),
                "completed_duration": int(played_seconds),
                "total_duration": int(total_seconds),
                "is_complete1": is_complete,
            }

            print(f"[DEBUG] user_id being sent: {str(user_id)}")
            # Right after getting expected params, print them:
            sig = inspect.signature(client.ontology.actions.create_progress_details)
            expected = list(sig.parameters.keys())
            print(f"[DEBUG] Expected params: {expected}")

            # Try CREATE first
            try:
                sig = inspect.signature(client.ontology.actions.create_progress_details)
                expected = list(sig.parameters.keys())
                kwargs = {p: param_values_create[p] for p in expected if p in param_values_create}
                print(f"[DEBUG] Calling create_progress_details with: {kwargs}")
                client.ontology.actions.create_progress_details(**kwargs)
                return {"status": "success"}

            except Exception as create_error:
                # If already exists → try MODIFY
                if "ObjectAlreadyExists" in str(create_error) or "CONFLICT" in str(create_error):
                    print("[DEBUG] Record exists, trying modify...")

                    # Find existing record
                    all_progress = client.ontology.objects.ProgressDetails.take(200)
                    existing = next(
                        (p for p in all_progress
                         if str(getattr(p, "course_id1", getattr(p, "course_id", ""))) == str(course_id)
                         and str(getattr(p, "lesson_id", getattr(p, "module_id", ""))) == str(module_id)
                         and str(getattr(p, "user_id1", getattr(p, "user_id", ""))) == str(user_id)),
                        None
                    )

                    if not existing:
                        # Try broader search
                        existing = next(
                            (p for p in all_progress
                             if str(getattr(p, "lesson_id", "")) == str(module_id)),
                            None
                        )

                    if existing:
                        # Use lesson_id as the record identifier
                        progress_id = int(module_id)

                        sig = inspect.signature(client.ontology.actions.modify_progress_deatils)
                        expected = list(sig.parameters.keys())

                        param_values_modify = {
                            "progress_details": progress_id,
                            "user_id1": str(user_id),
                            "course_id1": int(course_id),
                            "completed_duration": int(played_seconds),
                            "total_duration": int(total_seconds),
                            "is_complete1": is_complete,
                        }

                        kwargs = {p: param_values_modify[p] for p in expected if p in param_values_modify}
                        print(f"[DEBUG] Calling modify_progress_deatils with: {kwargs}")
                        client.ontology.actions.modify_progress_deatils(**kwargs)
                        return {"status": "success"}
                    else:
                        return {"status": "error", "message": "Record exists but couldn't find it to modify"}
                else:
                    raise create_error

    except Exception as e:
        print(f"[FOUNDRY ERROR] Progress update failed: {str(e)}")
        return {"status": "error", "message": f"Progress update failed: {str(e)}"}



def get_progress_details_for_course(course_id: str, user_id: str) -> Dict[str, Any]:
    """Get all progress details for a user in a course (from Foundry)."""
    if not is_foundry_configured():
        return {"total_modules": 0, "completed_modules": 0, "percentage": 0}

    try:
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()

            if not hasattr(client.ontology.objects, "ProgressDetails"):
                return {"total_modules": 0, "completed_modules": 0, "percentage": 0}

            all_progress = client.ontology.objects.ProgressDetails.take(200)

            # Filter for this user + course
            user_progress = [
                p for p in all_progress
                if str(getattr(p, "course_id1", getattr(p, "course_id", ""))) == str(course_id)
            ]

            # Count completed
            completed = [
                p for p in user_progress
                if getattr(p, "is_complete1", getattr(p, "is_complete", False)) == True
            ]

        # Get total modules for this course
        curriculum = _get_curriculum_for_course(course_id)
        total_modules = len(curriculum) if curriculum else 1

        completed_count = len(completed)
        percentage = round((completed_count / total_modules) * 100) if total_modules > 0 else 0

        return {
            "total_modules": total_modules,
            "completed_modules": completed_count,
            "percentage": percentage,
        }

    except Exception as e:
        print(f"[FOUNDRY ERROR] Progress details fetch failed: {str(e)}")
        return {"total_modules": 0, "completed_modules": 0, "percentage": 0}



# ═══════════════════════════════════════════════════════════════
# EVENT REGISTRATION (ACTION)
# ═══════════════════════════════════════════════════════════════

def register_for_event(event_id: str, user_id: str) -> Dict[str, Any]:
    """Register for a VanyarEvent (not courses)."""
    if not is_foundry_configured():
        return {"status": "success", "message": f"Registered for event {event_id} (Mock)"}

    try:
        import inspect
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            sig = inspect.signature(client.ontology.actions.register_for_event)
            params = list(sig.parameters.keys())

            param_values = {
                "event": event_id, "event_id": event_id, "eventId": event_id,
                "user": user_id, "user_id": user_id, "userId": user_id,
            }

            kwargs = {p: param_values[p] for p in params if p in param_values}
            client.ontology.actions.register_for_event(**kwargs)

        return {"status": "success", "message": f"Successfully registered user {user_id} for event {event_id}."}

    except Exception as e:
        print(f"[FOUNDRY ERROR] Registration failed: {str(e)}")
        return {"status": "error", "message": f"Registration failed: {str(e)}"}


def check_event_enrollment(event_id: str, user_id: str) -> bool:
    """Check if user is already registered for an event."""
    if not is_foundry_configured():
        return False

    try:
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            if not hasattr(client.ontology.objects, "VanyarEnrolment"):
                return False

            all_enrolments = client.ontology.objects.VanyarEnrolment.take(200)
            match = [
                e for e in all_enrolments
                if str(getattr(e, "user_id", "")) == str(user_id)
                and str(getattr(e, "event_id", "")) == str(event_id)
            ]
        return len(match) > 0

    except Exception as e:
        print(f"[FOUNDRY ERROR] Event enrollment check failed: {str(e)}")
        return False


# ═══════════════════════════════════════════════════════════════
# PUSH USER TO FOUNDRY
# ═══════════════════════════════════════════════════════════════

def push_user_to_foundry(
    user_id: str, email: str, full_name: str, role: str, learning_interest: str = ""
) -> Dict[str, Any]:
    if not is_foundry_configured():
        print(f"[FOUNDRY] Skipped user push (not configured): {email}")
        return {"status": "skipped", "message": "Foundry not configured."}

    try:
        import inspect
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            if not hasattr(client.ontology.actions, "create_vanyar_user"):
                return {"status": "error", "message": "create_vanyar_user action not in SDK."}

            sig = inspect.signature(client.ontology.actions.create_vanyar_user)
            expected_params = list(sig.parameters.keys())

            param_values = {
                "user_id": user_id, "userId": user_id, "user": user_id,
                "email": email,
                "name": full_name, "fullName": full_name, "userName": full_name,
                "role": role,
                "interest": learning_interest, "learningInterest": learning_interest,
            }

            kwargs = {p: param_values[p] for p in expected_params if p in param_values}
            client.ontology.actions.create_vanyar_user(**kwargs)

        print(f"[FOUNDRY] ✅ User synced: {email} ({user_id})")
        return {"status": "success", "message": f"User {email} synced to Foundry."}

    except Exception as e:
        print(f"[FOUNDRY ERROR] Failed to push user {email}: {str(e)}")
        return {"status": "error", "message": f"Foundry sync failed: {str(e)}"}


# ═══════════════════════════════════════════════════════════════
# USER LOOKUP
# ═══════════════════════════════════════════════════════════════

def search_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    if not is_foundry_configured():
        return None

    try:
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            if VanyarUser is None:
                return None
            prop = getattr(VanyarUser.object_type, "email")
            results = client.ontology.objects.VanyarUser.where(prop == email.lower()).take(1)
            if results:
                return flatten_osdk_object(results[0])
        return None

    except Exception as e:
        print(f"[FOUNDRY ERROR] Email lookup failed: {str(e)}")
        return None


# ═══════════════════════════════════════════════════════════════
# LEADERBOARD
# ═══════════════════════════════════════════════════════════════

def get_top_leaderboard(limit: int = 4) -> List[Dict[str, Any]]:
    if not is_foundry_configured():
        return _mock_leaderboard()[:limit]

    try:
        raw = _take_objects("VanyarLeaderboardEntry", limit)
        entries = [flatten_osdk_object(e) for e in raw]
        entries.sort(
            key=lambda x: int(x.get("score", 0) or x.get("pts", 0) or x.get("points", 0) or 0),
            reverse=True
        )
        return entries[:limit]

    except Exception as e:
        print(f"[FOUNDRY ERROR] Leaderboard fetch failed: {str(e)}")
        return _mock_leaderboard()[:limit]


def _mock_leaderboard() -> list:
    return [
        {"rank": 1, "name": "Alex Honnold", "pts": "2,450"},
        {"rank": 2, "name": "Sierra Blair", "pts": "2,210"},
        {"rank": 3, "name": "Clara Vance", "pts": "1,980"},
        {"rank": 4, "name": "Marcus Wright", "pts": "1,850"},
    ]


# ═══════════════════════════════════════════════════════════════
# REVIEWS
# ═══════════════════════════════════════════════════════════════

def get_all_reviews() -> List[Dict[str, Any]]:
    if not is_foundry_configured():
        return _mock_reviews()

    try:
        raw = _take_objects("ReviewsFeedback", 50)
        return [flatten_osdk_object(r) for r in raw]
    except Exception as e:
        print(f"[FOUNDRY ERROR] Reviews fetch failed: {str(e)}")
        return _mock_reviews()


def _mock_reviews() -> list:
    return [
        {"name": "Clara Vance", "role": "Student", "text": "The platform's deep integration with live datasets helped me land my job!"},
        {"name": "Marcus Wright", "role": "Participant", "text": "Incredibly smooth deployment workflows."},
    ]


# ═══════════════════════════════════════════════════════════════
# PLATFORM STATS
# ═══════════════════════════════════════════════════════════════

def get_platform_stats() -> Dict[str, Any]:
    if not is_foundry_configured():
        return {"total_events": 0, "total_tracks": 0, "total_users": 0, "total_hackathons": 0, "total_courses": 0}

    stats = {}
    try:
        for key, type_name in [
            ("total_events", "VanyarEvent"),
            ("total_tracks", "VanyarTrack"),
            ("total_users", "VanyarUser"),
            ("total_hackathons", "Hackathons"),
            ("total_courses", "Courses"),
        ]:
            try:
                records = _take_objects(type_name, 200)
                stats[key] = len(records)
            except Exception:
                stats[key] = 0
        return stats

    except Exception as e:
        print(f"[FOUNDRY ERROR] Stats failed: {str(e)}")
        return {"error": str(e)}

# ═══════════════════════════════════════════════════════════════
# HACKATHONS
# ═══════════════════════════════════════════════════════════════

def get_all_hackathons(status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all hackathons from Foundry."""
    if not is_foundry_configured():
        return []

    try:
        raw = _take_objects("Hackathons", 100)
        hackathons = []

        for h in raw:
            item = {
                "id": str(getattr(h, "course_id", "")),
                "title": getattr(h, "title1", None) or "Untitled Hackathon",
                "description": getattr(h, "description1", None),
                "start_date": str(getattr(h, "start_date", "")) if getattr(h, "start_date", None) else None,
                "end_date": str(getattr(h, "end_date", "")) if getattr(h, "end_date", None) else None,
                "status": getattr(h, "status1", None) or "Unknown",
                "mode": getattr(h, "mode1", None),
                "team_size": getattr(h, "team_size1", None),
                "participant_count": getattr(h, "participant_count1", None),
                "registrations": getattr(h, "registrations1", None),
                "registrations_deadline": str(getattr(h, "registrations_deadline", "")) if getattr(h, "registrations_deadline", None) else None,
                "rules": getattr(h, "rules1", None) or [],
                "difficulty_level": getattr(h, "difficulty_level1", None),
                "created_by": getattr(h, "created_by1", None),
                "content_id": getattr(h, "content_id1", None),
            }
            hackathons.append(item)

        # Apply status filter
        if status_filter:
            requested = [s.strip().lower() for s in status_filter.split(",")]
            hackathons = [h for h in hackathons if str(h.get("status", "")).lower() in requested]

        return hackathons

    except Exception as e:
        print(f"[FOUNDRY ERROR] Hackathons fetch failed: {str(e)}")
        return []


def get_hackathon_by_id(hackathon_id: str) -> Optional[Dict[str, Any]]:
    """Get single hackathon by ID with full details."""
    if not is_foundry_configured():
        return None

    try:
        try:
            pk_value = int(hackathon_id)
        except ValueError:
            pk_value = hackathon_id

        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            try:
                raw = client.ontology.objects.Hackathons.get(pk_value)
            except Exception:
                all_hackathons = client.ontology.objects.Hackathons.take(100)
                raw = next((h for h in all_hackathons if str(getattr(h, "course_id", "")) == str(hackathon_id)), None)

            if not raw:
                return None

            # Get teams for this hackathon
            teams = _get_teams_for_hackathon(hackathon_id)

            return {
                "id": str(getattr(raw, "course_id", "")),
                "title": getattr(raw, "title1", None) or "Untitled Hackathon",
                "description": getattr(raw, "description1", None),
                "start_date": str(getattr(raw, "start_date", "")) if getattr(raw, "start_date", None) else None,
                "end_date": str(getattr(raw, "end_date", "")) if getattr(raw, "end_date", None) else None,
                "status": getattr(raw, "status1", None) or "Unknown",
                "mode": getattr(raw, "mode1", None),
                "team_size": getattr(raw, "team_size1", None),
                "participant_count": getattr(raw, "participant_count1", None),
                "registrations": getattr(raw, "registrations1", None),
                "registrations_deadline": str(getattr(raw, "registrations_deadline", "")) if getattr(raw, "registrations_deadline", None) else None,
                "rules": getattr(raw, "rules1", None) or [],
                "difficulty_level": getattr(raw, "difficulty_level1", None),
                "created_by": getattr(raw, "created_by1", None),
                "content_id": getattr(raw, "content_id1", None),
                "teams": teams,
            }

    except Exception as e:
        print(f"[FOUNDRY ERROR] Hackathon detail fetch failed: {str(e)}")
        return None


def _get_teams_for_hackathon(hackathon_id: str) -> List[Dict[str, Any]]:
    """Get teams registered for a hackathon."""
    try:
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            if not hasattr(client.ontology.objects, "VanyarTeam"):
                return []

            all_teams = client.ontology.objects.VanyarTeam.take(50)
            matched = [
                t for t in all_teams
                if str(getattr(t, "event_id", "")) == str(hackathon_id)
            ]

            teams = []
            for t in matched:
                teams.append({
                    "id": getattr(t, "team_id", None),
                    "name": getattr(t, "name", None),
                    "captain_user_id": getattr(t, "captain_user_id", None),
                })
            return teams

    except Exception as e:
        print(f"[FOUNDRY ERROR] Teams fetch failed: {str(e)}")
        return []


def check_hackathon_registration(hackathon_id: str, user_id: str) -> bool:
    """Check if user is already registered for a hackathon."""
    if not is_foundry_configured():
        return False

    try:
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            if not hasattr(client.ontology.objects, "VanyarEnrolment"):
                return False

            all_enrolments = client.ontology.objects.VanyarEnrolment.take(200)
            match = [
                e for e in all_enrolments
                if str(getattr(e, "user_id", "")) == str(user_id)
                and str(getattr(e, "event_id", "")) == str(hackathon_id)
            ]
        return len(match) > 0

    except Exception as e:
        print(f"[FOUNDRY ERROR] Hackathon registration check failed: {str(e)}")
        return False


def register_for_hackathon(hackathon_id: str, user_id: str) -> Dict[str, Any]:
    """Register user for a hackathon using create_enrolment action."""
    import uuid

    if not is_foundry_configured():
        return {"status": "success", "registration_id": str(uuid.uuid4())}

    try:
        import inspect
        registration_id = str(uuid.uuid4())

        with AllowBetaFeatures():
            client = foundry_osdk.get_client()

            if not hasattr(client.ontology.actions, "create_enrolment"):
                return {"status": "error", "message": "create_enrolment action not available"}

            sig = inspect.signature(client.ontology.actions.create_enrolment)
            expected = list(sig.parameters.keys())
            print(f"[DEBUG] create_enrolment expects: {expected}")

            param_values = {
                "user_id": user_id, "userId": user_id, "user": user_id,
                "status": "registered", "Status": "registered",
                "event_id": str(hackathon_id), "eventId": str(hackathon_id), "eventid": str(hackathon_id),
                "event": str(hackathon_id), "course_id": str(hackathon_id), "courseId": str(hackathon_id),
                "enrollment_id": registration_id, "enrolment_id": registration_id,
                "enrollmentId": registration_id, "enrolmentId": registration_id,
            }

            kwargs = {p: param_values[p] for p in expected if p in param_values}
            print(f"[DEBUG] Calling create_enrolment with: {kwargs}")
            client.ontology.actions.create_enrolment(**kwargs)

        return {"status": "success", "registration_id": registration_id}

    except Exception as e:
        print(f"[FOUNDRY ERROR] Hackathon registration failed: {str(e)}")
        return {"status": "error", "message": f"Registration failed: {str(e)}"}


def get_user_team(user_id: str) -> Optional[Dict[str, Any]]:
    """Get the user's team (where they are captain)."""
    if not is_foundry_configured():
        return None

    try:
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            if not hasattr(client.ontology.objects, "VanyarTeam"):
                return None

            all_teams = client.ontology.objects.VanyarTeam.take(50)
            my_team = next(
                (t for t in all_teams if str(getattr(t, "captain_user_id", "")) == str(user_id)),
                None
            )

            if not my_team:
                return None

            return {
                "id": getattr(my_team, "team_id", None),
                "name": getattr(my_team, "name", None),
                "captain_user_id": getattr(my_team, "captain_user_id", None),
                "event_id": getattr(my_team, "event_id", None),
                "is_lead": True,
            }

    except Exception as e:
        print(f"[FOUNDRY ERROR] User team fetch failed: {str(e)}")
        return None


# app/integrations/palantir/foundry_service.py
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

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


# ═══════════════════════════════════════════════════════════════
# HACKATHONS
# ═══════════════════════════════════════════════════════════════

def get_all_hackathons() -> List[Dict[str, Any]]:
    if not is_foundry_configured():
        return []

    try:
        raw = _take_objects("Hackathons", 100)
        return [flatten_osdk_object(h) for h in raw]
    except Exception as e:
        print(f"[FOUNDRY ERROR] Hackathons fetch failed: {str(e)}")
        return []

######################################################################################################
# # ═══════════════════════════════════════════════════════════════
# # COURSES — LIST, SEARCH, DETAIL
# # ═══════════════════════════════════════════════════════════════

# def get_all_courses(
#     offset: int = 0,
#     limit: int = 6,
#     category: Optional[str] = None,
#     level: Optional[str] = None
# ) -> Dict[str, Any]:
#     if not is_foundry_configured():
#         return {"courses": [], "total": 0, "offset": offset, "limit": limit}

#     try:
#         raw = _take_objects("Courses", 200)
#         courses = [flatten_osdk_object(c) for c in raw]

#         if category:
#             courses = [c for c in courses if str(c.get("category", "")).lower() == category.lower()]
#         if level:
#             courses = [c for c in courses if str(c.get("level", "")).lower() == level.lower()]

#         total = len(courses)
#         paginated = courses[offset:offset + limit]
#         return {"courses": paginated, "total": total, "offset": offset, "limit": limit}

#     except Exception as e:
#         print(f"[FOUNDRY ERROR] Courses fetch failed: {str(e)}")
#         return {"courses": [], "total": 0, "offset": offset, "limit": limit}


# def search_courses_catalog(query_str: str, limit: int = 10) -> Dict[str, Any]:
#     if not is_foundry_configured():
#         return {"results": [], "query": query_str, "count": 0}

#     try:
#         raw = _take_objects("Courses", 200)
#         courses = [flatten_osdk_object(c) for c in raw]

#         q = query_str.lower()
#         results = [
#             c for c in courses
#             if q in str(c.get("course_name1", "")).lower()
#             or q in str(c.get("name", "")).lower()
#             or q in str(c.get("title", "")).lower()
#         ]
#         return {"results": results[:limit], "query": query_str, "count": len(results[:limit])}

#     except Exception as e:
#         print(f"[FOUNDRY ERROR] Course search failed: {str(e)}")
#         return {"results": [], "query": query_str, "count": 0}


# def get_single_course(course_id: str) -> Optional[Dict[str, Any]]:
#     if not is_foundry_configured():
#         return None

#     try:
#         try:
#             pk_value = int(course_id)
#         except ValueError:
#             pk_value = course_id

#         with AllowBetaFeatures():
#             client = foundry_osdk.get_client()
#             if not hasattr(client.ontology.objects, "Courses"):
#                 return None

#             try:
#                 raw = client.ontology.objects.Courses.get(pk_value)
#                 return flatten_osdk_object(raw)
#             except Exception:
#                 pass

#             if Courses is not None:
#                 for pk_name in ["course_id", "id", "courseId"]:
#                     if hasattr(Courses.object_type, pk_name):
#                         prop = getattr(Courses.object_type, pk_name)
#                         results = client.ontology.objects.Courses.where(prop == pk_value).take(1)
#                         if results:
#                             return flatten_osdk_object(results[0])
#         return None

#     except Exception as e:
#         print(f"[FOUNDRY ERROR] Single course fetch failed: {str(e)}")
#         return None

####################################################################################################################333

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
def get_single_course(course_id: str) -> Optional[Dict[str, Any]]:
        if not is_foundry_configured():
            return None

        try:
            try:
                pk_value = int(course_id)
            except ValueError:
                pk_value = course_id

            with AllowBetaFeatures():
                client = foundry_osdk.get_client()
                if not hasattr(client.ontology.objects, "Courses"):
                    return None

                try:
                    raw = client.ontology.objects.Courses.get(pk_value)
                    return flatten_osdk_object(raw)
                except Exception:
                    pass

                if Courses is not None:
                    for pk_name in ["course_id", "id", "courseId"]:
                        if hasattr(Courses.object_type, pk_name):
                            prop = getattr(Courses.object_type, pk_name)
                            results = client.ontology.objects.Courses.where(prop == pk_value).take(1)
                            if results:
                                return flatten_osdk_object(results[0])
            return None
        except Exception as e:
            print(f"[FOUNDRY ERROR] Single course fetch failed: {str(e)}")
            return None

def get_course_modules(course_id: str) -> Dict[str, Any]:
    """
    Get full course curriculum with modules, lessons, video URLs, and materials.
    Currently maps 1 course = 1 module = 1 lesson (from Courses object).
    """

    if not is_foundry_configured():
        return {"course": {"id": course_id, "title": "", "description": "", "curriculum": []}}

    try:
        course = get_single_course(course_id=course_id)
        if not course:
            return {"course": {"id": course_id, "title": "", "description": "", "curriculum": []}}

        # Build materials list
        materials = []
        if course.get("derived") or course.get("course_resources1"):
            materials.append({
                "id": f"m-{course_id}-pdf",
                "title": "Course PDF Notes",
                "type": "pdf",
                "meta": "PDF Document",
            })

        # Build the lesson from the course data
        lesson = {
            "id": f"{course_id}-1",
            "title": course.get("title") or course.get("course_name1", "Lesson 1"),
            "video_url": course.get("course_url1") or "",
            "summary": course.get("about_the_course") or course.get("description", ""),
            "materials": materials,
        }

        # Build the module (currently 1 module per course)
        module = {
            "id": int(course_id) if course_id.isdigit() else course_id,
            "title": course.get("title") or course.get("course_name1", "Module 1"),
            "lessons": [lesson],
        }

        # Build the full response
        return {
            "course": {
                "id": str(course.get("course_id", course_id)),
                "title": course.get("title") or course.get("course_name1", ""),
                "description": course.get("description") or course.get("about_the_course", ""),
                "curriculum": [module],
            }
        }

    except Exception as e:
        print(f"[FOUNDRY ERROR] Get course modules failed: {str(e)}")

def get_module_content(course_id: str, module_id: str) -> Optional[Dict[str, Any]]:
    """Get module content — video URL and PDF resource."""
    if not is_foundry_configured():
        return None

    try:
        course = get_single_course(course_id=course_id)
        if not course:
            return None

        return {
            "courseId": course_id,
            "moduleId": module_id,
            "title": course.get("title") or course.get("course_name1"),
            "video_url": course.get("course_url1"),
            "pdf_resource": course.get("derived") or course.get("course_resources1"),
            "content_id": course.get("content_id"),
        }

    except Exception as e:
        print(f"[FOUNDRY ERROR] Get module content failed: {str(e)}")
        return None

def get_course_pdf_content(course_id: str) -> tuple:
    """Fetch PDF content from Foundry using OSDK media property."""
    if not is_foundry_configured():
        return (None, None)

    try:
        try:
            pk_value = int(course_id)
        except ValueError:
            pk_value = course_id

        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            course_obj = client.ontology.objects.Courses.get(pk_value)

            # Read the media property directly via OSDK
            content = course_obj.course_resources1.read()
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

def get_course_quiz(course_id: str, module_id: str = None) -> Dict[str, Any]:
    """Fetch quiz questions for a course from Quizes object. Returns structured quiz format."""
    empty_quiz = {
        "quiz": {
            "id": f"quiz_{course_id}",
            "title": "Module Test",
            "path": "",
            "time_limit": 10,
            "questions": [],
        }
    }

    if not is_foundry_configured():
        return empty_quiz

    try:
        # Get course info for title/path
        course = get_single_course(course_id=course_id)
        course_title = ""
        if course:
            course_title = course.get("title") or course.get("course_name1", "")

        # Fetch quiz questions from Foundry
        raw = _take_objects("Quizes", 200)

        course_questions = [
            q for q in raw
            if str(getattr(q, "course_id", "")) == str(course_id)
        ]

        # Build questions array
        questions = []
        for idx, q in enumerate(course_questions):
            flat = flatten_osdk_object(q)

            # Get options as a list of strings
            options_raw = flat.get("multiple_choice", [])
            if isinstance(options_raw, str):
                import json
                try:
                    options_raw = json.loads(options_raw)
                except (json.JSONDecodeError, ValueError):
                    options_raw = [options_raw]

            if not isinstance(options_raw, list):
                options_raw = []

            # Determine correct answer as letter (a, b, c, d)
            answer_raw = flat.get("answer", [])
            if isinstance(answer_raw, str):
                answer_raw = [answer_raw.strip()]
            elif not isinstance(answer_raw, list):
                answer_raw = [str(answer_raw)]

            # Convert to lowercase letter
            correct_letter = "a"
            if answer_raw:
                correct_val = answer_raw[0].strip().upper()
                # If already a letter (A, B, C, D)
                if correct_val in ("A", "B", "C", "D", "E"):
                    correct_letter = correct_val.lower()
                # If it's a number (1, 2, 3, 4) → convert to letter
                elif correct_val.isdigit():
                    num = int(correct_val)
                    letter_map = {1: "a", 2: "b", 3: "c", 4: "d", 5: "e"}
                    correct_letter = letter_map.get(num, "a")
                # If it's index-based (0, 1, 2, 3)
                else:
                    # Try matching answer text to options
                    for i, opt in enumerate(options_raw):
                        if str(opt).strip().lower() == correct_val.lower():
                            index_map = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e"}
                            correct_letter = index_map.get(i, "a")
                            break

            # Format question ID as q_001, q_002, etc.
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
                "title": f"Module Test: {course_title}",
                "path": course_title,
                "time_limit": 10,
                "questions": questions,
            }
        }

    except Exception as e:
        print(f"[FOUNDRY ERROR] Quiz fetch failed: {str(e)}")
        return empty_quiz



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

        course_questions = [
            q for q in raw
            if str(getattr(q, "course_id", "")) == str(course_id)
        ]

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
# COURSES — PROGRESS
# ═══════════════════════════════════════════════════════════════

def get_course_progress(course_id: str, user_id: str) -> Dict[str, Any]:
    """Get enrollment status and completion for a course."""
    if not is_foundry_configured():
        return {"courseId": course_id, "userId": user_id, "status": "not enrolled"}

    try:
        with AllowBetaFeatures():
            client = foundry_osdk.get_client()
            if not hasattr(client.ontology.objects, "VanyarEnrolment"):
                return {"courseId": course_id, "userId": user_id, "status": "not enrolled"}

            all_enrolments = client.ontology.objects.VanyarEnrolment.take(200)
            match = [
                e for e in all_enrolments
                if str(getattr(e, "user_id", "")) == str(user_id)
                and str(getattr(e, "event_id", "")) == str(course_id)
            ]

        if not match:
            return {"courseId": course_id, "userId": user_id, "status": "not enrolled"}

        enrollment = flatten_osdk_object(match[0])
        return {
            "courseId": course_id,
            "userId": user_id,
            "status": enrollment.get("status", "in progress"),
            "enrollment_id": enrollment.get("enrolment_id"),
            "enrolled_at": enrollment.get("enrolled_at"),
            "completed_at": enrollment.get("completed_at"),
        }

    except Exception as e:
        print(f"[FOUNDRY ERROR] Course progress failed: {str(e)}")
        return {"courseId": course_id, "userId": user_id, "status": "unknown", "error": str(e)}


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


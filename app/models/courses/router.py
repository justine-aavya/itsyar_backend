

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional
import requests
import os

from app.api.deps import get_current_user
from app.models.user import User
from app.integrations.palantir import foundry_service

from .schemas import TestSubmissionRequest

router = APIRouter()


def error_response(status_code: int, message: str):
    return JSONResponse(
        status_code=status_code,
        content={"error": {"data": {"message": message}}}
    )


def _get_foundry_token():
    """Get OAuth token from Foundry for proxying media."""
    foundry_url = os.getenv("FOUNDRY_URL", "").rstrip("/")
    client_id = os.getenv("FOUNDRY_CLIENT_ID")
    client_secret = os.getenv("FOUNDRY_CLIENT_SECRET")

    token_resp = requests.post(
        f"{foundry_url}/multipass/api/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=10
    )
    return token_resp.json().get("access_token")

##########################################################################################################################
# ═══════════════════════════════════════════════════════════════
# LIST / SEARCH / MY
# ═══════════════════════════════════════════════════════════════

# @router.get("/", status_code=status.HTTP_200_OK)
# def list_courses(
#     offset: int = 0,
#     limit: int = 6,
#     category: Optional[str] = None,
#     level: Optional[str] = None,
#     current_user: User = Depends(get_current_user),
# ):
#     """List all available courses."""
#     try:
#         result = foundry_service.get_all_courses(offset=offset, limit=limit, category=category, level=level)

#         courses = []
#         for c in result.get("courses", []):
#             courses.append({
#                 "id": str(c.get("course_id", c.get("id", ""))),
#                 "title": c.get("title") or c.get("course_name1", "Untitled"),
#                 "tag": c.get("tag", "General"),
#                 "duration": c.get("duration1", "Self-paced"),
#                 "instructor": c.get("instructor", "ItsYar Team"),
#                 "description": c.get("description", ""),
#                 "image": c.get("image", ""),
#                 "badge": c.get("badge"),
#                 "level": c.get("level", "Beginner"),
#                 "enrolled": False,
#             })

#         return {"success": True, "courses": courses, "total": result.get("total", 0), "offset": offset, "limit": limit}

#     except Exception as e:
#         return error_response(500, f"Failed to fetch courses: {str(e)}")


# @router.get("/search", status_code=status.HTTP_200_OK)
# def search_courses(
#     q: str = Query(..., min_length=2),
#     limit: int = 10,
#     current_user: User = Depends(get_current_user),
# ):
#     """Search courses by keyword."""
#     try:
#         result = foundry_service.search_courses_catalog(query_str=q, limit=limit)
#         return {"success": True, **result}
#     except Exception as e:
#         return error_response(500, f"Search failed: {str(e)}")

###################################################################################################################

# ═══════════════════════════════════════════════════════════════
# LOOK (COMBINED LIST + SEARCH)
# ═══════════════════════════════════════════════════════════════

@router.get("/look", status_code=status.HTTP_200_OK)
def look_courses(
    q: Optional[str] = None,
    offset: int = 0,
    limit: int = 10,
    category: Optional[str] = None, #tag
    level: Optional[str] = None, #experience level
    current_user: User = Depends(get_current_user),
):
    """Combined listing + search. If q is provided, filters by keyword."""
    try:
        result = foundry_service.look_courses(
            query=q,
            offset=offset,
            limit=limit,
            category=category,
            level=level,
        )
        return {"success": True, **result}

    except Exception as e:
        return error_response(500, f"Failed to fetch courses: {str(e)}")



@router.get("/my_learning", status_code=status.HTTP_200_OK)
def get_my_courses(
    current_user: User = Depends(get_current_user),
):
    """Get courses the current user is enrolled in."""
    try:
        result = foundry_service.get_user_enrolled_courses(user_id=str(current_user.id))

        my_courses = []
        for enrollment in result.get("courses", []):
            course_id = str(enrollment.get("event_id", enrollment.get("course_id", "")))

            try:
                int(course_id)
            except ValueError:
                continue

            course_detail = foundry_service.get_single_course(course_id=course_id)
            title = "Unknown Course"
            if course_detail:
                title = course_detail.get("title") or course_detail.get("course_name1", "Unknown Course")

            enrollment_status = enrollment.get("status", "in progress")
            progress = 100 if enrollment_status == "completed" else 0

            my_courses.append({
                "id": course_id,
                "title": title,
                "level": "Beginner",
                "lessons": "1 Module",
                "progress": progress,
                "category": "code",
                "status": enrollment_status,
                "enrolledAt": enrollment.get("enrolled_at"),
                "completedAt": enrollment.get("completed_at"),
            })

        return {"success": True, "courses": my_courses, "count": len(my_courses)}

    except Exception as e:
        return error_response(500, f"Failed to fetch enrolled courses: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# COURSE DETAIL
# ═══════════════════════════════════════════════════════════════

@router.get("/{course_id}", status_code=status.HTTP_200_OK)
def get_course_details(
    course_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get single course details — includes video, PDF, summary, progress."""
    try:
        course = foundry_service.get_single_course(course_id=course_id)
        if not course:
            return error_response(404, "Course resource not found")

        enrollment = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
        is_enrolled = enrollment.get("isEnrolled", False)

        # Get completion percentage
        completion_percentage = 0
        if is_enrolled:
            progress = foundry_service.get_course_progress(course_id=course_id, user_id=str(current_user.id))
            if progress.get("status") == "completed":
                completion_percentage = 100

        # Build materials array
        materials = []
        if course.get("derived") or course.get("course_resources1"):
            materials.append({
                "id": f"pdf_{course_id}",
                "title": "Course PDF Notes",
                "type": "pdf",
                "meta": "PDF Document",
                "url": f"/api/courses/{course_id}/pdf"
            })

        return {
            "success": True,
            "data": {
                "id": str(course.get("course_id", course_id)),
                "title": course.get("title") or course.get("course_name1", ""),
                "tag": course.get("tag", "General"),
                "category": course.get("tag", "DEVELOPMENT"),
                "description": course.get("description", ""),
                "longDescription": course.get("about_the_course"),
                "summary": course.get("about_the_course") or course.get("description", ""),
                "level": course.get("level", "Beginner"),
                "modulesCount": 1,
                "duration": course.get("duration1", "Self-paced"),
                "thumbnail": course.get("image", ""),
                "instructor": course.get("instructor", "ItsYar Team"),
                #"videoUrl": f"/static/videos/course_{course_id}.mp4",
                "pdfResource": f"/api/courses/{course_id}/pdf",
                "contentId": course.get("content_id"),
                "curriculum": course.get("curriculum1"),
                "takeaways": course.get("takeaways"),
                "courseCompletionPercentage": completion_percentage,
                "materials": materials,
                "isEnrolled": is_enrolled,

            }
        }

    except Exception as e:
        return error_response(500, f"Failed to fetch course: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# VIDEO & PDF PROXY
# ═══════════════════════════════════════════════════════════════

# @router.get("/{course_id}/video", status_code=status.HTTP_200_OK)
# def stream_course_video(
#     course_id: str,
#     current_user: User = Depends(get_current_user),
# ):
#     """Proxy video from Foundry — streams to frontend without Foundry auth."""
#     try:
#         status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
#         if not status_check.get("isEnrolled"):
#             return error_response(403, "You must be enrolled to access video")

#         course = foundry_service.get_single_course(course_id=course_id)
#         if not course or not course.get("course_url1"):
#             return error_response(404, "Video not found")

#         video_url = course.get("course_url1")
#         access_token = _get_foundry_token()

#         response = requests.get(
#             video_url,
#             headers={"Authorization": f"Bearer {access_token}"},
#             stream=True,
#             timeout=30
#         )

#         if response.status_code != 200:
#             return error_response(502, "Failed to fetch video from Foundry")

#         return StreamingResponse(
#             response.iter_content(chunk_size=8192),
#             media_type=response.headers.get("content-type", "video/mp4"),
#             headers={
#                 "Content-Disposition": f"inline; filename=course_{course_id}_video.mp4"
#             }
#         )

#     except Exception as e:
#         return error_response(500, f"Video streaming failed: {str(e)}")


@router.get("/{course_id}/pdf", status_code=status.HTTP_200_OK)
def stream_course_pdf(
    course_id: str,
    current_user: User = Depends(get_current_user),
):
    """Stream PDF from Palantir Foundry."""
    try:
        status_check = foundry_service.check_user_enrollment(
            course_id=course_id, user_id=str(current_user.id)
        )
        if not status_check.get("isEnrolled"):
            return error_response(403, "You must be enrolled to access PDF")

        # Use OSDK to read media directly
        content, content_type = foundry_service.get_course_pdf_content(course_id)

        if not content:
            return error_response(404, "PDF resource not found in Foundry")

        from fastapi.responses import Response as RawResponse
        return RawResponse(
            content=content,
            media_type=content_type or "application/pdf",
            headers={
                "Content-Disposition": f"inline; filename=course_{course_id}_notes.pdf"
            },
        )

    except Exception as e:
        return error_response(500, f"PDF streaming failed: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# ENROLLMENT
# ═══════════════════════════════════════════════════════════════

@router.post("/{course_id}/enroll", status_code=status.HTTP_201_CREATED)
def enroll_in_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
):
    """Enroll in a course."""
    try:
        status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
        if status_check.get("isEnrolled"):
            return error_response(409, "You are already enrolled in this course")

        result = foundry_service.execute_course_enrollment_action(
            course_id=course_id,
            user_id=str(current_user.id)
        )
        if not result or result.get("status") == "error":
            return error_response(500, result.get("message", "Enrollment failed"))

        return {"success": True, **result}

    except Exception as e:
        return error_response(500, f"Enrollment failed: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# MODULES
# ═══════════════════════════════════════════════════════════════

@router.get("/{course_id}/modules", status_code=status.HTTP_200_OK)
def get_course_modules(
    course_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get full course curriculum — modules, lessons, videos, materials."""
    try:
        status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
        if not status_check.get("isEnrolled"):
            return error_response(403, "You must be enrolled to view modules")

        result = foundry_service.get_course_modules(course_id=course_id)
        return {"success": True, **result}

    except Exception as e:
        return error_response(500, f"Failed to fetch modules: {str(e)}")


@router.get("/{course_id}/modules/{module_id}/content", status_code=status.HTTP_200_OK)
def get_module_content(
    course_id: str,
    module_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get module content (video + PDF). Enrolled users only."""
    try:
        status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
        if not status_check.get("isEnrolled"):
            return error_response(403, "You must be enrolled to access content")

        content = foundry_service.get_module_content(course_id=course_id, module_id=module_id)
        if not content:
            return error_response(404, "Module content not found")

        return {"success": True, "data": content}

    except Exception as e:
        return error_response(500, f"Failed to fetch content: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# QUIZ
# ═══════════════════════════════════════════════════════════════

@router.get("/{course_id}/modules/{module_id}/quiz", status_code=status.HTTP_200_OK)
def get_module_quiz(
    course_id: str,
    module_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get quiz questions for a module. Enrolled users only."""
    try:
        status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
        if not status_check.get("isEnrolled"):
            return error_response(403, "You must be enrolled to access the quiz")

        result = foundry_service.get_course_quiz(course_id=course_id, module_id=module_id)
        return {"success": True, **result}

    except Exception as e:
        return error_response(500, f"Failed to fetch quiz: {str(e)}")



@router.post("/{course_id}/modules/{module_id}/quiz/submit", status_code=status.HTTP_200_OK)
def submit_module_quiz(
    course_id: str,
    module_id: str,
    payload: TestSubmissionRequest,
    current_user: User = Depends(get_current_user),
):
    """Submit quiz answers. Auto-graded. If passed → course marked complete."""
    try:
        status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
        if not status_check.get("isEnrolled"):
            return error_response(403, "You must be enrolled to submit the quiz")

        result = foundry_service.grade_and_complete_course(
            course_id=course_id,
            module_id=module_id,
            user_id=str(current_user.id),
            submission_data=payload
        )
        return {"success": True, **result}

    except Exception as e:
        return error_response(500, f"Quiz submission failed: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# PROGRESS
# ═══════════════════════════════════════════════════════════════

@router.get("/{course_id}/progress", status_code=status.HTTP_200_OK)
def get_course_progress(
    course_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get enrollment status and completion info."""
    try:
        result = foundry_service.get_course_progress(course_id=course_id, user_id=str(current_user.id))
        return {"success": True, **result}
    except Exception as e:
        return error_response(500, f"Failed to fetch progress: {str(e)}")



# from fastapi import APIRouter, Depends, Query, status
# from fastapi.responses import JSONResponse, StreamingResponse
# from typing import Optional
# import requests
# import os

# from app.api.deps import get_current_user
# from app.models.user import User
# from app.integrations.palantir import foundry_service

# from .schemas import TestSubmissionRequest

# router = APIRouter()


# def error_response(status_code: int, message: str):
#     return JSONResponse(
#         status_code=status_code,
#         content={"error": {"data": {"message": message}}}
#     )


# def _get_foundry_token():
#     """Get OAuth token from Foundry for proxying media."""
#     foundry_url = os.getenv("FOUNDRY_URL", "").rstrip("/")
#     client_id = os.getenv("FOUNDRY_CLIENT_ID")
#     client_secret = os.getenv("FOUNDRY_CLIENT_SECRET")

#     token_resp = requests.post(
#         f"{foundry_url}/multipass/api/oauth2/token",
#         data={
#             "grant_type": "client_credentials",
#             "client_id": client_id,
#             "client_secret": client_secret,
#         },
#         timeout=10
#     )
#     return token_resp.json().get("access_token")


# # ═══════════════════════════════════════════════════════════════
# # LIST / SEARCH / MY
# # ═══════════════════════════════════════════════════════════════

# @router.get("/", status_code=status.HTTP_200_OK)
# def list_courses(
#     offset: int = 0,
#     limit: int = 6,
#     category: Optional[str] = None,
#     level: Optional[str] = None,
#     current_user: User = Depends(get_current_user),
# ):
#     """List all available courses."""
#     try:
#         result = foundry_service.get_all_courses(offset=offset, limit=limit, category=category, level=level)

#         courses = []
#         for c in result.get("courses", []):
#             courses.append({
#                 "id": str(c.get("course_id", c.get("id", ""))),
#                 "title": c.get("title") or c.get("course_name1", "Untitled"),
#                 "tag": c.get("tag", "General"),
#                 "duration": c.get("duration1", "Self-paced"),
#                 "instructor": c.get("instructor", "ItsYar Team"),
#                 "description": c.get("description", ""),
#                 "image": c.get("image", ""),
#                 "badge": c.get("badge"),
#                 "level": c.get("level", "Beginner"),
#                 "enrolled": False,
#             })

#         return {"success": True, "courses": courses, "total": result.get("total", 0), "offset": offset, "limit": limit}

#     except Exception as e:
#         return error_response(500, f"Failed to fetch courses: {str(e)}")


# @router.get("/search", status_code=status.HTTP_200_OK)
# def search_courses(
#     q: str = Query(..., min_length=2),
#     limit: int = 10,
#     current_user: User = Depends(get_current_user),
# ):
#     """Search courses by keyword."""
#     try:
#         result = foundry_service.search_courses_catalog(query_str=q, limit=limit)
#         return {"success": True, **result}
#     except Exception as e:
#         return error_response(500, f"Search failed: {str(e)}")


# @router.get("/my", status_code=status.HTTP_200_OK)
# def get_my_courses(
#     current_user: User = Depends(get_current_user),
# ):
#     """Get courses the current user is enrolled in."""
#     try:
#         result = foundry_service.get_user_enrolled_courses(user_id=str(current_user.id))

#         my_courses = []
#         for enrollment in result.get("courses", []):
#             course_id = str(enrollment.get("event_id", enrollment.get("course_id", "")))

#             try:
#                 int(course_id)
#             except ValueError:
#                 continue

#             course_detail = foundry_service.get_single_course(course_id=course_id)
#             title = "Unknown Course"
#             if course_detail:
#                 title = course_detail.get("title") or course_detail.get("course_name1", "Unknown Course")

#             enrollment_status = enrollment.get("status", "in progress")
#             progress = 100 if enrollment_status == "completed" else 0

#             my_courses.append({
#                 "id": course_id,
#                 "title": title,
#                 "level": "Beginner",
#                 "lessons": "1 Module",
#                 "progress": progress,
#                 "category": "code",
#                 "status": enrollment_status,
#                 "enrolledAt": enrollment.get("enrolled_at"),
#                 "completedAt": enrollment.get("completed_at"),
#             })

#         return {"success": True, "courses": my_courses, "count": len(my_courses)}

#     except Exception as e:
#         return error_response(500, f"Failed to fetch enrolled courses: {str(e)}")


# # ═══════════════════════════════════════════════════════════════
# # COURSE DETAIL
# # ═══════════════════════════════════════════════════════════════

# @router.get("/{course_id}", status_code=status.HTTP_200_OK)
# def get_course_details(
#     course_id: str,
#     current_user: User = Depends(get_current_user),
# ):
#     """Get single course details — includes video, PDF, summary, progress."""
#     try:
#         course = foundry_service.get_single_course(course_id=course_id)
#         if not course:
#             return error_response(404, "Course resource not found")

#         enrollment = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
#         is_enrolled = enrollment.get("isEnrolled", False)

#         # Get completion percentage
#         completion_percentage = 0
#         if is_enrolled:
#             progress = foundry_service.get_course_progress(course_id=course_id, user_id=str(current_user.id))
#             if progress.get("status") == "completed":
#                 completion_percentage = 100

#         # Build materials array
#         materials = []
#         if course.get("derived") or course.get("course_resources1"):
#             materials.append({
#                 "id": f"pdf_{course_id}",
#                 "title": "Course PDF Notes",
#                 "type": "pdf",
#                 "meta": "PDF Document",
#                 "url": f"/api/courses/{course_id}/pdf"
#             })

#         return {
#             "success": True,
#             "data": {
#                 "id": str(course.get("course_id", course_id)),
#                 "title": course.get("title") or course.get("course_name1", ""),
#                 "tag": course.get("tag", "General"),
#                 "category": course.get("tag", "DEVELOPMENT"),
#                 "description": course.get("description", ""),
#                 "longDescription": course.get("about_the_course"),
#                 "summary": course.get("about_the_course") or course.get("description", ""),
#                 "level": course.get("level", "Beginner"),
#                 "modulesCount": 1,
#                 "duration": course.get("duration1", "Self-paced"),
#                 "thumbnail": course.get("image", ""),
#                 "instructor": course.get("instructor", "ItsYar Team"),
#                 "videoUrl": f"/api/courses/{course_id}/video",
#                 "pdfResource": f"/api/courses/{course_id}/pdf",
#                 "contentId": course.get("content_id"),
#                 "curriculum": course.get("curriculum1"),
#                 "takeaways": course.get("takeaways"),
#                 "courseCompletionPercentage": completion_percentage,
#                 "materials": materials,
#                 "isEnrolled": is_enrolled,

#             }
#         }

#     except Exception as e:
#         return error_response(500, f"Failed to fetch course: {str(e)}")


# # ═══════════════════════════════════════════════════════════════
# # VIDEO & PDF PROXY
# # ═══════════════════════════════════════════════════════════════

# def _iter_stream(stream, chunk_size=8192):
#     """Yield chunks from a stream object."""
#     while True:
#         chunk = stream.read(chunk_size)
#         if not chunk:
#             break
#         yield chunk


# @router.get("/{course_id}/video", status_code=status.HTTP_200_OK)
# def stream_course_video(
#     course_id: str,
#     current_user: User = Depends(get_current_user),
# ):
#     """Proxy video from Foundry — tries SDK stream first, falls back to HTTP proxy."""
#     try:
#         status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
#         if not status_check.get("isEnrolled"):
#             return error_response(403, "You must be enrolled to access video")

#         # ── Primary: SDK-based streaming ──
#         try:
#             stream, content_type = foundry_service.open_course_video(course_id=course_id)
#             if stream is not None:
#                 return StreamingResponse(
#                     _iter_stream(stream),
#                     media_type=content_type or "video/mp4",
#                     headers={"Content-Disposition": f"inline; filename=course_{course_id}_video.mp4"}
#                 )
#         except Exception:
#             pass  # Fall through to HTTP fallback

#         # ── Fallback: HTTP proxy with OAuth token ──
#         course = foundry_service.get_single_course(course_id=course_id)
#         if not course or not course.get("course_url1"):
#             return error_response(404, "Video not found")

#         video_url = course.get("course_url1")
#         access_token = _get_foundry_token()

#         response = requests.get(
#             video_url,
#             headers={"Authorization": f"Bearer {access_token}"},
#             stream=True,
#             timeout=30
#         )

#         if response.status_code != 200:
#             return error_response(502, "Failed to fetch video from Foundry")

#         return StreamingResponse(
#             response.iter_content(chunk_size=8192),
#             media_type=response.headers.get("content-type", "video/mp4"),
#             headers={"Content-Disposition": f"inline; filename=course_{course_id}_video.mp4"}
#         )

#     except Exception as e:
#         return error_response(500, f"Video streaming failed: {str(e)}")


# @router.get("/{course_id}/modules/{module_id}/video")
# def stream_module_video(
#     course_id: str,
#     module_id: str,
#     current_user: User = Depends(get_current_user),
# ):
#     """Stream the module video. Enrolled users only.
    
#     Tries SDK-based media read first, falls back to HTTP proxy.
#     """
#     try:
#         status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
#         if not status_check.get("isEnrolled"):
#             return error_response(403, "You must be enrolled to watch this video")

#         # ── Primary: SDK-based streaming ──
#         try:
#             stream, content_type = foundry_service.open_course_video(course_id=course_id)
#             if stream is not None:
#                 return StreamingResponse(
#                     _iter_stream(stream),
#                     media_type=content_type or "video/mp4",
#                     headers={"Content-Disposition": f"inline; filename=course_{course_id}_module_{module_id}_video.mp4"}
#                 )
#         except Exception:
#             pass  # Fall through to HTTP fallback

#         # ── Fallback: HTTP proxy with OAuth token ──
#         course = foundry_service.get_single_course(course_id=course_id)
#         if not course or not course.get("course_url1"):
#             return error_response(404, "Video not available for this course")

#         video_url = course.get("course_url1")
#         access_token = _get_foundry_token()

#         response = requests.get(
#             video_url,
#             headers={"Authorization": f"Bearer {access_token}"},
#             stream=True,
#             timeout=30
#         )

#         if response.status_code != 200:
#             return error_response(502, "Failed to fetch video from Foundry")

#         return StreamingResponse(
#             response.iter_content(chunk_size=8192),
#             media_type=response.headers.get("content-type", "video/mp4"),
#             headers={"Content-Disposition": f"inline; filename=course_{course_id}_module_{module_id}_video.mp4"}
#         )

#     except Exception as e:
#         return error_response(500, f"Failed to stream video: {str(e)}")


# @router.get("/{course_id}/pdf", status_code=status.HTTP_200_OK)
# def stream_course_pdf(
#     course_id: str,
#     current_user: User = Depends(get_current_user),
# ):
#     """Stream PDF from Palantir Foundry."""
#     try:
#         status_check = foundry_service.check_user_enrollment(
#             course_id=course_id, user_id=str(current_user.id)
#         )
#         if not status_check.get("isEnrolled"):
#             return error_response(403, "You must be enrolled to access PDF")

#         # Use OSDK to read media directly
#         content, content_type = foundry_service.get_course_pdf_content(course_id)

#         if not content:
#             return error_response(404, "PDF resource not found in Foundry")

#         from fastapi.responses import Response as RawResponse
#         return RawResponse(
#             content=content,
#             media_type=content_type or "application/pdf",
#             headers={
#                 "Content-Disposition": f"inline; filename=course_{course_id}_notes.pdf"
#             },
#         )

#     except Exception as e:
#         return error_response(500, f"PDF streaming failed: {str(e)}")


# # ═══════════════════════════════════════════════════════════════
# # ENROLLMENT
# # ═══════════════════════════════════════════════════════════════

# @router.post("/{course_id}/enroll", status_code=status.HTTP_201_CREATED)
# def enroll_in_course(
#     course_id: str,
#     current_user: User = Depends(get_current_user),
# ):
#     """Enroll in a course."""
#     try:
#         status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
#         if status_check.get("isEnrolled"):
#             return error_response(409, "You are already enrolled in this course")

#         result = foundry_service.execute_course_enrollment_action(
#             course_id=course_id,
#             user_id=str(current_user.id)
#         )
#         if not result or result.get("status") == "error":
#             return error_response(500, result.get("message", "Enrollment failed"))

#         return {"success": True, **result}

#     except Exception as e:
#         return error_response(500, f"Enrollment failed: {str(e)}")


# # ═══════════════════════════════════════════════════════════════
# # MODULES
# # ═══════════════════════════════════════════════════════════════

# @router.get("/{course_id}/modules", status_code=status.HTTP_200_OK)
# def get_course_modules(
#     course_id: str,
#     current_user: User = Depends(get_current_user),
# ):
#     """List modules for a course."""
#     try:
#         status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
#         if not status_check.get("isEnrolled"):
#             return error_response(403, "You must be enrolled to view modules")

#         result = foundry_service.get_course_modules(course_id=course_id)
#         return {"success": True, **result}

#     except Exception as e:
#         return error_response(500, f"Failed to fetch modules: {str(e)}")


# @router.get("/{course_id}/modules/{module_id}/content", status_code=status.HTTP_200_OK)
# def get_module_content(
#     course_id: str,
#     module_id: str,
#     current_user: User = Depends(get_current_user),
# ):
#     """Get module content (video + PDF). Enrolled users only."""
#     try:
#         status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
#         if not status_check.get("isEnrolled"):
#             return error_response(403, "You must be enrolled to access content")

#         content = foundry_service.get_module_content(course_id=course_id, module_id=module_id)
#         if not content:
#             return error_response(404, "Module content not found")

#         return {"success": True, "data": content}

#     except Exception as e:
#         return error_response(500, f"Failed to fetch content: {str(e)}")


# # ═══════════════════════════════════════════════════════════════
# # QUIZ
# # ═══════════════════════════════════════════════════════════════

# @router.get("/{course_id}/modules/{module_id}/quiz", status_code=status.HTTP_200_OK)
# def get_module_quiz(
#     course_id: str,
#     module_id: str,
#     current_user: User = Depends(get_current_user),
# ):
#     """Get quiz questions for a module. Enrolled users only."""
#     try:
#         status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
#         if not status_check.get("isEnrolled"):
#             return error_response(403, "You must be enrolled to access the quiz")

#         result = foundry_service.get_course_quiz(course_id=course_id, module_id=module_id)
#         return {"success": True, **result}

#     except Exception as e:
#         return error_response(500, f"Failed to fetch quiz: {str(e)}")


# @router.post("/{course_id}/modules/{module_id}/quiz/submit", status_code=status.HTTP_200_OK)
# def submit_module_quiz(
#     course_id: str,
#     module_id: str,
#     payload: TestSubmissionRequest,
#     current_user: User = Depends(get_current_user),
# ):
#     """Submit quiz answers. Auto-graded. If passed → course marked complete."""
#     try:
#         status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
#         if not status_check.get("isEnrolled"):
#             return error_response(403, "You must be enrolled to submit the quiz")

#         result = foundry_service.grade_and_complete_course(
#             course_id=course_id,
#             module_id=module_id,
#             user_id=str(current_user.id),
#             submission_data=payload
#         )
#         return {"success": True, **result}

#     except Exception as e:
#         return error_response(500, f"Quiz submission failed: {str(e)}")


# # ═══════════════════════════════════════════════════════════════
# # PROGRESS
# # ═══════════════════════════════════════════════════════════════

# @router.get("/{course_id}/progress", status_code=status.HTTP_200_OK)
# def get_course_progress(
#     course_id: str,
#     current_user: User = Depends(get_current_user),
# ):
#     """Get enrollment status and completion info."""
#     try:
#         result = foundry_service.get_course_progress(course_id=course_id, user_id=str(current_user.id))
#         return {"success": True, **result}
#     except Exception as e:
#         return error_response(500, f"Failed to fetch progress: {str(e)}")

from fastapi import APIRouter, Depends, Query, status, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse, Response
from fastapi.responses import Response as RawResponse
from fastapi.responses import StreamingResponse

from typing import Optional
import requests
import os
import urllib.parse

from app.models.courses.schemas import TestSubmissionRequest,LessonProgressRequest



from app.api.deps import get_current_user, require_student_role
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

@router.get("", status_code=status.HTTP_200_OK)
def list_courses(
    offset: int = 0,
    limit: int = 6,
    category: Optional[str] = None,
    level: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """List all available courses with pagination and optional filters."""
    try:
        # Role gate: only Students can view course catalog
        require_student_role(current_user)

        # Fetch courses from Foundry with filters
        result = foundry_service.get_all_courses(offset=offset, limit=limit, category=category, level=level)

        # Format each course for frontend
        courses = []
        for c in result.get("courses", []):
            courses.append({
                "id": str(c.get("course_id", c.get("id", ""))),
                "course_id": str(c.get("course_id", c.get("id", ""))),
                "module_id": 1,
                "title": c.get("title") or c.get("course_name1", "Untitled"),
                "tag": c.get("tag", "General"),
                "duration": c.get("duration") or c.get("duration1", "Self-paced"),
                "instructor": c.get("instructor", "ItsYar Team"),
                "description": c.get("description", ""),
                "image": c.get("image", ""),
                "badge": c.get("badge"),
                "level": c.get("level", "Beginner"),
                "enrolled": False,
            })

        # Success response
        return {"success": True, "courses": courses, "total": result.get("total", 0), "offset": offset, "limit": limit}

    except HTTPException:
        # Let role check 403 pass through (don't catch as 500)
        raise
    except Exception as e:
        return error_response(500, f"Failed to fetch courses: {str(e)}")

@router.get("/search", status_code=status.HTTP_200_OK)
def search_courses(
    q: str = Query(..., min_length=2),
    limit: int = 10,
    current_user: User = Depends(get_current_user),
):
    """Search courses by keyword. Requires Student role."""
    try:
        # Role gate: only Students can search courses
        require_student_role(current_user)

        # Search courses by keyword in Foundry
        result = foundry_service.search_courses_catalog(query_str=q, limit=limit)

        # Success response
        return {"success": True, **result}

    except HTTPException:
        # Let role check 403 pass through
        raise
    except Exception as e:
        return error_response(500, f"Search failed: {str(e)}")


@router.get("/my-learnings", status_code=status.HTTP_200_OK)
def get_my_courses(
    current_user: User = Depends(get_current_user),
):
    """Get courses the current user is enrolled in. Requires Student role."""
    try:
        # Role gate: only Students have enrolled courses
        require_student_role(current_user)

        # Fetch enrollments from Foundry
        result = foundry_service.get_user_enrolled_courses(user_id=str(current_user.id))

        # Get valid course IDs (to filter out hackathon/event enrollments)
        valid_course_ids = foundry_service.get_valid_course_ids()

        # Build enriched course list with details
        my_courses = []
        for enrollment in result.get("courses", []):
            course_id = str(enrollment.get("event_id", enrollment.get("course_id", "")))

            # Skip non-numeric course IDs
            try:
                int(course_id)
            except ValueError:
                continue

            # Skip if not a real course (might be hackathon/event enrollment)
            if course_id not in valid_course_ids:
                continue

            # Fetch full course details for title
            course_detail = foundry_service.get_single_course(course_id=course_id)
            title = "Unknown Course"
            if course_detail:
                title = course_detail.get("title") or course_detail.get("course_name1", "Unknown Course")

            # Derive progress from enrollment status
            enrollment_status = enrollment.get("status", "in progress")
            progress = 100 if enrollment_status.lower() == "completed" else 0

            my_courses.append({
                "id": course_id,
                "course_id": course_id,
                "module_id": 1,
                "title": title,
                "level": "Beginner",
                "lessons": "1 Module",
                "progress": progress,
                "category": "code",
                "status": enrollment_status,
                "enrolledAt": enrollment.get("enrolled_at"),
                "completedAt": enrollment.get("completed_at"),
            })

        # Success response
        return {"success": True, "courses": my_courses, "count": len(my_courses)}

    except HTTPException:
        raise
    except Exception as e:
        return error_response(500, f"Failed to fetch enrolled courses: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# CERTIFICATE
# ═══════════════════════════════════════════════════════════════

##for completion check
# @router.get("/{course_id}/certificate", status_code=status.HTTP_200_OK)
# def get_certificate_info(
#     course_id: str,
#     current_user: User = Depends(get_current_user),
# ):
#     """Get certificate metadata. Only accessible if course is completed."""
#     try:
#         require_student_role(current_user)

#         # Get certificate info (returns None if not completed)
#         cert_info = foundry_service.get_certificate_info(
#             course_id=course_id,
#             user_id=str(current_user.id),
#             user_name=current_user.full_name
#         )

#         if not cert_info:
#             return error_response(403, "Complete the course to earn your certificate")

#         return {"success": True, "certificate": cert_info}

#     except HTTPException:
#         raise
#     except Exception as e:
#         return error_response(500, f"Certificate failed: {str(e)}")

@router.get("/{course_id}/certificate", status_code=status.HTTP_200_OK)
def get_certificate_info(
    course_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get certificate metadata."""
    try:
        require_student_role(current_user)

        cert_info = foundry_service.get_certificate_info(
            course_id=course_id,
            user_id=str(current_user.id),
            user_name=current_user.full_name
        )

        if not cert_info:
            return error_response(404, "Certificate info not found")

        return {"success": True, "certificate": cert_info}

    except HTTPException:
        raise
    except Exception as e:
        return error_response(500, f"Certificate failed: {str(e)}")





# ## Single module
# # ═══════════════════════════════════════════════════════════════
# # VIDEO — Stream from Foundry Media Property
# # ═══════════════════════════════════════════════════════════════

# @router.get("/video/{course_id}", status_code=status.HTTP_200_OK)
# def stream_course_video(
#     course_id: str,
#     #current_user: User = Depends(get_current_user),
# ):
#     """Stream video from Palantir Foundry. Opens inline in browser."""
#     try:
#         # Role gate: only Students can access video
#         #require_student_role(current_user)

#         # Enrollment gate: must be enrolled
#         #status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
#         # if not status_check.get("isEnrolled"):
#         #     return error_response(403, "You must be enrolled to access video")

#         # # Fetch video bytes from Foundry OSDK
#         content, content_type = foundry_service.get_course_video_content(course_id)

#         if not content:
#             return error_response(404, "Video resource not found in Foundry")

#         from fastapi.responses import Response as RawResponse
#         return RawResponse(
#             content=content,
#             media_type=content_type or "video/mp4",
#             headers={
#                 "Content-Disposition": f"inline; filename=course_{course_id}_video.mp4",
#                 "Content-Type": "video/mp4",
#                 "Accept-Ranges": "bytes",
#                 "Cache-Control": "public, max-age=3600",
#             },
#         )

#     except HTTPException:
#         raise
#     except Exception as e:
#         return error_response(500, f"Video streaming failed: {str(e)}")
    

## for multiple courses
# ═══════════════════════════════════════════════════════════════
# VIDEO — Per module
# ═══════════════════════════════════════════════════════════════

@router.get("/video/{course_id}/{module_id}", status_code=status.HTTP_200_OK)
def stream_module_video(course_id: str, module_id: str, request: Request):
    """Stream video with range request support for instant playback."""
    try:
        media_stream, content_type, size_bytes = foundry_service.get_course_video_content(course_id, module_id)
        if not media_stream:
            return error_response(404, "Video not found for this module")

        # Check for Range header
        range_header = request.headers.get("range")

        if range_header and size_bytes:
            # Parse range: "bytes=0-65535"
            range_str = range_header.replace("bytes=", "")
            parts = range_str.split("-")
            start = int(parts[0])
            end = int(parts[1]) if parts[1] else size_bytes - 1

            # Clamp end to file size
            end = min(end, size_bytes - 1)
            length = end - start + 1

            # Seek to start position and read the range
            media_stream.seek(start)
            chunk = media_stream.read(length)

            return Response(
                content=chunk,
                status_code=206,
                media_type="video/mp4",
                headers={
                    "Content-Range": f"bytes {start}-{end}/{size_bytes}",
                    "Content-Length": str(length),
                    "Accept-Ranges": "bytes",
                    "Content-Type": "video/mp4",
                    "Cache-Control": "public, max-age=3600",
                },
            )

        # No range requested — stream full file
        def chunk_generator():
            while True:
                chunk = media_stream.read(65536)
                if not chunk:
                    break
                yield chunk

        headers = {
            "Content-Disposition": f"inline; filename=course_{course_id}_module_{module_id}_video.mp4",
            "Content-Type": "video/mp4",
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=3600",
        }
        if size_bytes:
            headers["Content-Length"] = str(size_bytes)

        return StreamingResponse(
            chunk_generator(),
            media_type=content_type or "video/mp4",
            headers=headers,
        )
    except Exception as e:
        return error_response(500, f"Video streaming failed: {str(e)}")


@router.get("/video/{course_id}", status_code=status.HTTP_200_OK)
def stream_course_video(course_id: str, request: Request):
    """Stream video (first module) with range request support."""
    try:
        media_stream, content_type, size_bytes = foundry_service.get_course_video_content(course_id)
        if not media_stream:
            return error_response(404, "Video not found")

        range_header = request.headers.get("range")

        if range_header and size_bytes:
            range_str = range_header.replace("bytes=", "")
            parts = range_str.split("-")
            start = int(parts[0])
            end = int(parts[1]) if parts[1] else size_bytes - 1
            end = min(end, size_bytes - 1)
            length = end - start + 1

            media_stream.seek(start)
            chunk = media_stream.read(length)

            return Response(
                content=chunk,
                status_code=206,
                media_type="video/mp4",
                headers={
                    "Content-Range": f"bytes {start}-{end}/{size_bytes}",
                    "Content-Length": str(length),
                    "Accept-Ranges": "bytes",
                    "Content-Type": "video/mp4",
                    "Cache-Control": "public, max-age=3600",
                },
            )

        def chunk_generator():
            while True:
                chunk = media_stream.read(65536)
                if not chunk:
                    break
                yield chunk

        headers = {
            "Content-Disposition": f"inline; filename=course_{course_id}_video.mp4",
            "Content-Type": "video/mp4",
            "Accept-Ranges": "bytes",
            "Cache-Control": "public, max-age=3600",
        }
        if size_bytes:
            headers["Content-Length"] = str(size_bytes)

        return StreamingResponse(
            chunk_generator(),
            media_type=content_type or "video/mp4",
            headers=headers,
        )
    except Exception as e:
        return error_response(500, f"Video streaming failed: {str(e)}")


@router.get("/thumbnail/{course_id}", status_code=status.HTTP_200_OK)
def get_course_thumbnail(course_id: str):
    """Serve course thumbnail image from Foundry."""
    try:
        content, content_type = foundry_service.get_course_thumbnail_content(course_id)

        if not content:
            return error_response(404, "Thumbnail not found")

        from fastapi.responses import Response as RawResponse
        return RawResponse(
            content=content,
            media_type=content_type or "image/jpeg",
            headers={"Cache-Control": "public, max-age=86400"},
        )

    except Exception as e:
        return error_response(500, f"Thumbnail failed: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# COURSE DETAIL
# ═══════════════════════════════════════════════════════════════

@router.get("/{course_id}", status_code=status.HTTP_200_OK)
def get_course_details(
    course_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get single course details — includes video, PDF, summary, progress. Requires Student role."""
    try:
        # Role gate: only Students can view course details
        require_student_role(current_user)

        # Fetch course from Foundry
        course = foundry_service.get_single_course(course_id=course_id)
        if not course:
            return error_response(404, "Course resource not found")

        # Check if current user is enrolled
        enrollment = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
        is_enrolled = enrollment.get("isEnrolled", False)
        curriculum_data = foundry_service._get_curriculum_for_course(course_id)

        # Get completion percentage and status
        completion_percentage = 0
        status_value = "not enrolled"
        if is_enrolled:
            progress = foundry_service.get_course_progress(course_id=course_id, user_id=str(current_user.id))
            completion_percentage = progress.get("percentage", 0)
            status_value = progress.get("status", "in progress")


        # Build materials array
        materials = []
        if course.get("derived") or course.get("course_resources1"):
            materials.append({
                "id": f"pdf_{course_id}",
                "title": "Course PDF Notes",
                "type": "pdf",
                "meta": "PDF Document",
                "url": f"/api/courses/{course_id}/pdf",
                "pdf_status": "success",
            })
        else:
            materials.append({
                "id": f"pdf_{course_id}",
                "title": "Course PDF Notes",
                "type": "pdf",
                "meta": "PDF Document",
                "url": None,
                "pdf_status": "unavailable",
            })

        # Success response
        return {
            "success": True,
            "data": {
                "id": str(course.get("course_id", course_id)),
                "course_id": str(course.get("course_id", course_id)),
                #"module_id": curriculum_data[0]["id"] if curriculum_data else course_id,
                "module_id": curriculum_data[0].get("id", course_id) if curriculum_data else course_id,
                "title": course.get("title") or course.get("course_name1", ""),
                "include": course.get("include", []),
                "tag": course.get("tag", "General"),
                "description": course.get("description", ""),
                "longDescription": course.get("about_the_course"),
                "summary": course.get("about_the_course") or course.get("description", ""),
                "level": course.get("level", "Beginner"),
                "thumbnail": f"/api/courses/thumbnail/{course_id}",
                "instructor": course.get("instructor", "ItsYar Team"),
                "videoUrl": f"/api/courses/video/{course_id}",
                "pdfResource": f"/api/courses/{course_id}/pdf",
                "modulesCount": len(curriculum_data) or 1,
                "curriculum": curriculum_data,
                "takeaways": course.get("takeaways"),
                "courseCompletionPercentage": completion_percentage,
                "status": status_value,
                "isEnrolled": is_enrolled,
                "materials": materials
                
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        return error_response(500, f"Failed to fetch course: {str(e)}")

# ## Single modle
# # ═══════════════════════════════════════════════════════════════
# # PDF 
# # ═══════════════════════════════════════════════════════════════

# @router.get("/{course_id}/pdf", status_code=status.HTTP_200_OK)
# def stream_course_pdf(
#     course_id: str,
#     #current_user: User = Depends(get_current_user),
# ):
#     """Stream PDF from Foundry. Opens inline in browser (not download)."""
#     try:
#         # Fetch PDF bytes from Foundry
#         content, content_type = foundry_service.get_course_pdf_content(course_id)

#         if not content:
#             return error_response(404, "PDF resource not found in Foundry")


#         return RawResponse(
#             content=content,
#             media_type="application/pdf",
#             headers={
#                 # "inline" = view in browser, "attachment" = force download
#                 "Content-Disposition": f"inline; filename=course_{course_id}_notes.pdf",
#                 "Content-Type": "application/pdf",
#             },
#         )

#     # except HTTPException:
#     #     raise
#     except Exception as e:
#         return error_response(500, f"PDF streaming failed: {str(e)}")

## for multiple courses
# ═══════════════════════════════════════════════════════════════
# PDF — Per module
# ═══════════════════════════════════════════════════════════════

@router.get("/{course_id}/pdf/{module_id}", status_code=status.HTTP_200_OK)
def stream_module_pdf(course_id: str, module_id: str):
    """Stream PDF for a specific module."""
    try:
        content, content_type = foundry_service.get_course_pdf_content(course_id, module_id)
        if not content:
            return error_response(404, "PDF not found for this module")

        return RawResponse(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=course_{course_id}_module_{module_id}_notes.pdf"},
        )
    except Exception as e:
        return error_response(500, f"PDF streaming failed: {str(e)}")


@router.get("/{course_id}/pdf", status_code=status.HTTP_200_OK)
def stream_course_pdf(course_id: str):
    """Stream PDF for course (first module). Fallback."""
    try:
        content, content_type = foundry_service.get_course_pdf_content(course_id)
        if not content:
            return error_response(404, "PDF not found")

        return RawResponse(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": f"inline; filename=course_{course_id}_notes.pdf"},
        )
    except Exception as e:
        return error_response(500, f"PDF streaming failed: {str(e)}")

# ═══════════════════════════════════════════════════════════════
# MARK COURSE COMPLETE
# ═══════════════════════════════════════════════════════════════

@router.post("/{course_id}/complete", status_code=status.HTTP_200_OK)
def mark_course_complete(
    course_id: str,
    current_user: User = Depends(get_current_user),
):
    """Manually mark a course as complete. Requires Student role + enrollment."""
    try:
        # Role gate
        require_student_role(current_user)

        # Enrollment gate
        status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
        if not status_check.get("isEnrolled"):
            return error_response(403, "You must be enrolled to complete this course")

        # Mark complete in Foundry
        result = foundry_service.mark_course_complete(course_id=course_id, user_id=str(current_user.id))

        if result.get("status") == "error":
            return error_response(500, result.get("message", "Failed to mark complete"))

        return {"success": True, **result}

    except HTTPException:
        raise
    except Exception as e:
        return error_response(500, f"Mark complete failed: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# ENROLLMENT
# ═══════════════════════════════════════════════════════════════

@router.post("/{course_id}/enroll", status_code=status.HTTP_201_CREATED)
def enroll_in_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
):
    """Enroll in a course. Requires Student role."""
    try:
        # Role gate: only Students can enroll in courses
        require_student_role(current_user)

        # Check if already enrolled (prevent duplicate enrollment)
        status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
        if status_check.get("isEnrolled"):
            return error_response(409, "You are already enrolled in this course")

        # Execute enrollment action in Foundry
        result = foundry_service.execute_course_enrollment_action(
            course_id=course_id,
            user_id=str(current_user.id)
        )

        # Check if Foundry action returned an error
        if not result or result.get("status") == "error":
            return error_response(500, result.get("message", "Enrollment failed"))

        # Success response
        return {"success": True, **result}

    except HTTPException:
        # Let role check 403 pass through
        raise
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
    """Get full course curriculum — modules, lessons, videos, materials. Requires Student role + enrollment."""
    try:
        # Role gate: only Students can access course content
        require_student_role(current_user)

        # Enrollment gate: must be enrolled to view modules
        status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
        if not status_check.get("isEnrolled"):
            return error_response(403, "You must be enrolled to view modules")

        # Fetch full curriculum from Foundry
        result = foundry_service.get_course_modules(course_id=course_id)

        # Success response
        return {"success": True, **result}

    except HTTPException:
        # Let role check 403 pass through
        raise
    except Exception as e:
        return error_response(500, f"Failed to fetch modules: {str(e)}")

# ## Single course
# @router.get("/{course_id}/modules/{module_id}/content", status_code=status.HTTP_200_OK)
# def get_module_content(
#     course_id: str,
#     module_id: str,
#     current_user: User = Depends(get_current_user),
# ):
#     """Get module content (video + PDF). Requires Student role + enrollment."""
#     try:
#         # Role gate: only Students can access course content
#         require_student_role(current_user)

#         # Enrollment gate: must be enrolled to access content
#         status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
#         if not status_check.get("isEnrolled"):
#             return error_response(403, "You must be enrolled to access content")

#         # Fetch module content (video URL + PDF) from Foundry
#         content = foundry_service.get_module_content(course_id=course_id, module_id=module_id)
#         if not content:
#             return error_response(404, "Module content not found")

#         # Success response
#         return {"success": True, "data": content}

#     except HTTPException:
#         # Let role check 403 pass through
#         raise
#     except Exception as e:
#         return error_response(500, f"Failed to fetch content: {str(e)}")


## Multiple Courses
@router.get("/{course_id}/modules/{module_id}/content", status_code=status.HTTP_200_OK)
def get_module_content(
    course_id: str,
    module_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get module content (video + PDF). Requires Student role + enrollment."""
    try:
        require_student_role(current_user)

        status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
        if not status_check.get("isEnrolled"):
            return error_response(403, "You must be enrolled to access content")

        content = foundry_service.get_module_content(course_id=course_id, module_id=module_id)
        if not content:
            return error_response(404, "Module content not found")

        return {"success": True, "data": content}

    except HTTPException:
        raise
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
    """Get quiz questions for a module. Requires Student role + enrollment."""
    try:
        # Role gate: only Students can access quizzes
        require_student_role(current_user)

        # Enrollment gate: must be enrolled to access the quiz
        status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
        if not status_check.get("isEnrolled"):
            return error_response(403, "You must be enrolled to access the quiz")

        # Fetch quiz questions from Foundry
        result = foundry_service.get_course_quiz(course_id=course_id, module_id=module_id)

        # Success response
        return {"success": True, **result}

    except HTTPException:
        # Let role check 403 pass through
        raise
    except Exception as e:
        return error_response(500, f"Failed to fetch quiz: {str(e)}")


@router.post("/{course_id}/modules/{module_id}/quiz/submit", status_code=status.HTTP_200_OK)
def submit_module_quiz(
    course_id: str,
    module_id: str,
    payload: TestSubmissionRequest,
    current_user: User = Depends(get_current_user),
):
    """Submit quiz answers. Auto-graded. If passed → course marked complete. Requires Student role + enrollment."""
    try:
        # Role gate: only Students can submit quizzes
        require_student_role(current_user)

        # Enrollment gate: must be enrolled to submit
        status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
        if not status_check.get("isEnrolled"):
            return error_response(403, "You must be enrolled to submit the quiz")

        # Grade quiz and auto-complete course if passed (≥70%)
        result = foundry_service.grade_and_complete_course(
            course_id=course_id,
            module_id=module_id,
            user_id=str(current_user.id),
            submission_data=payload
        )

        # Check if grading itself returned an error
        if result.get("status") == "error":
            return error_response(500, result.get("message", "Quiz grading failed"))

        # Success response
        return {"success": True, **result}

    except HTTPException:
        # Let role check 403 pass through
        raise
    except Exception as e:
        return error_response(500, f"Quiz submission failed: {str(e)}")


# ═══════════════════════════════════════════════════════════════
# PROGRESS
# ═══════════════════════════════════════════════════════════════

@router.post("/{course_id}/modules/{module_id}/progress", status_code=status.HTTP_200_OK)
def update_lesson_progress(
    course_id: str,
    module_id: str,
    payload: LessonProgressRequest,
    current_user: User = Depends(get_current_user),
):
    """Update video watch progress. Sends to Foundry ProgressDetails."""
    try:
        require_student_role(current_user)
        user_id = str(current_user.id)

        # Calculate if complete (> 90% watched)
        is_complete = False
        if payload.total_seconds > 0 and (payload.played_seconds / payload.total_seconds) > 0.9:
            is_complete = True
        elif payload.is_completed:
            is_complete = True

        # Send to Foundry
        result = foundry_service.update_progress_details(
            course_id=course_id,
            module_id=module_id,
            user_id=user_id,
            played_seconds=payload.played_seconds,
            total_seconds=payload.total_seconds,
            is_complete=is_complete,
        )

        if result.get("status") == "error":
            return error_response(500, result.get("message", "Progress update failed"))

        # Get updated course completion percentage
        progress_data = foundry_service.get_progress_details_for_course(course_id, user_id)

        return {
            "success": True,
            "module_id": module_id,
            "course_id": course_id,
            "is_completed": is_complete,
            "played_seconds": payload.played_seconds,
            "total_seconds": payload.total_seconds,
            "course_completion_percentage": progress_data.get("percentage", 0),
            "completed_modules": progress_data.get("completed_modules", 0),
            "total_modules": progress_data.get("total_modules", 0),
        }

    except HTTPException:
        raise
    except Exception as e:
        return error_response(500, f"Progress update failed: {str(e)}")



@router.get("/{course_id}/progress", status_code=status.HTTP_200_OK)
def get_course_progress(
    course_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get overall course progress from Foundry."""
    try:
        require_student_role(current_user)
        user_id = str(current_user.id)

        # Get Foundry enrollment status
        foundry_progress = foundry_service.get_course_progress(course_id=course_id, user_id=user_id)

        # Get video progress from Foundry ProgressDetails
        progress_data = foundry_service.get_progress_details_for_course(course_id, user_id)

        # Determine overall percentage
        foundry_status = foundry_progress.get("status", "not enrolled")
        if foundry_status.lower() == "completed":
            percentage = 100
        else:
            percentage = progress_data.get("percentage", 0)

        return {
            "success": True,
            "courseId": course_id,
            "userId": user_id,
            "status": foundry_status,
            "percentage": percentage,
            "total_modules": progress_data.get("total_modules", 0),
            "completed_modules": progress_data.get("completed_modules", 0),
            "video_percentage": progress_data.get("percentage", 0),
            "enrollment_id": foundry_progress.get("enrollment_id"),
            "enrolled_at": foundry_progress.get("enrolled_at"),
            "completed_at": foundry_progress.get("completed_at"),
        }

    except HTTPException:
        raise
    except Exception as e:
        return error_response(500, f"Failed to fetch progress: {str(e)}")


# @router.get("/{course_id}/progress", status_code=status.HTTP_200_OK)
# def get_course_progress(
#     course_id: str,
#     current_user: User = Depends(get_current_user),
# ):
#     """Get enrollment status and completion info. Requires Student role."""
#     try:
#         # Role gate: only Students can check course progress
#         require_student_role(current_user)

#         # Fetch progress from Foundry enrollment records
#         result = foundry_service.get_course_progress(course_id=course_id, user_id=str(current_user.id))

#         # Success response
#         return {"success": True, **result}

#     except HTTPException:
#         # Let role check 403 pass through
#         raise
#     except Exception as e:
#         return error_response(500, f"Failed to fetch progress: {str(e)}")


# @router.post("/{course_id}/modules/{module_id}/progress", status_code=status.HTTP_200_OK)
# def update_lesson_progress(
#     course_id: str,
#     module_id: str,
#     payload: LessonProgressRequest,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db),
# ):
#     """Update video watch progress for a module. Auto-completes at 90%."""
#     try:
#         # Auth: only Students can track progress
#         require_student_role(current_user)
#         user_id = str(current_user.id)

#         # STEP 1: Find existing record or create new one
#         progress = db.query(LessonProgress).filter(
#             LessonProgress.user_id == user_id,
#             LessonProgress.course_id == course_id,
#             LessonProgress.module_id == module_id,
#         ).first()

#         if not progress:
#             progress = LessonProgress(
#                 user_id=user_id,
#                 course_id=course_id,
#                 module_id=module_id,
#             )
#             db.add(progress)

#         # STEP 2: Update watch time
#         progress.played_seconds = payload.played_seconds
#         progress.total_seconds = payload.total_seconds

#         # STEP 3: Auto-complete if > 90% watched
#         if payload.total_seconds > 0 and (payload.played_seconds / payload.total_seconds) > 0.9:
#             progress.is_completed = True
#         elif payload.is_completed:
#             progress.is_completed = True

#         # STEP 4: Save to database
#         db.commit()
#         db.refresh(progress)

#         # STEP 5: Calculate course completion percentage
#         curriculum = foundry_service._get_curriculum_for_course(course_id)
#         total_modules = len(curriculum) if curriculum else 1

#         completed_count = db.query(LessonProgress).filter(
#             LessonProgress.user_id == user_id,
#             LessonProgress.course_id == course_id,
#             LessonProgress.is_completed == True,
#         ).count()

#         course_completion_percentage = round((completed_count / total_modules) * 100)

#         # STEP 6: Return response
#         return {
#             "success": True,
#             "module_id": module_id,
#             "course_id": course_id,
#             "is_completed": progress.is_completed,
#             "played_seconds": progress.played_seconds,
#             "total_seconds": progress.total_seconds,
#             "course_completion_percentage": course_completion_percentage,
#             "completed_modules": completed_count,
#             "total_modules": total_modules,
#         }

#     except HTTPException:
#         raise
#     except Exception as e:
#         return error_response(500, f"Progress update failed: {str(e)}")

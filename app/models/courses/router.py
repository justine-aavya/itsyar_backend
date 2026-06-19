# from fastapi import APIRouter, Depends, HTTPException, Query, status
# from typing import Optional

# from app.api.deps import get_current_user
# from app.models.user import User
# from app.integrations.palantir import foundry_service

# from .schemas import TestSubmissionRequest

# router = APIRouter()


# @router.get("/", status_code=status.HTTP_200_OK)
# def list_courses(
#     offset: int = 0,
#     limit: int = 6,
#     category: Optional[str] = None,
#     level: Optional[str] = None,
#     current_user: User = Depends(get_current_user),
# ):
#     """List all available courses."""
#     return foundry_service.get_all_courses(offset=offset, limit=limit, category=category, level=level)


# @router.get("/search", status_code=status.HTTP_200_OK)
# def search_courses(
#     q: str = Query(..., min_length=2),
#     limit: int = 10,
#     current_user: User = Depends(get_current_user),
# ):
#     """Search courses by keyword."""
#     return foundry_service.search_courses_catalog(query_str=q, limit=limit)


# @router.get("/my", status_code=status.HTTP_200_OK)
# def get_my_courses(
#     current_user: User = Depends(get_current_user),
# ):
#     """Get courses the current user is enrolled in."""
#     return foundry_service.get_user_enrolled_courses(user_id=str(current_user.id))


# @router.get("/{course_id}", status_code=status.HTTP_200_OK)
# def get_course_details(
#     course_id: str,
#     current_user: User = Depends(get_current_user),
# ):
#     """Get single course details including enrollment status."""
#     course = foundry_service.get_single_course(course_id=course_id)
#     if not course:
#         raise HTTPException(status_code=404, detail="Course resource not found")

#     # Include enrollment info (renamed from /enrollment endpoint)
#     enrollment = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))

#     return {
#         **course,
#         "isEnrolled": enrollment.get("isEnrolled", False),
#     }


# @router.post("/{course_id}/enroll", status_code=status.HTTP_201_CREATED)
# def enroll_in_course(
#     course_id: str,
#     current_user: User = Depends(get_current_user),
# ):
#     """Enroll in a course. Calls create_enrolment action in Foundry."""
#     status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
#     if status_check.get("isEnrolled"):
#         raise HTTPException(
#             status_code=409,
#             detail="You are already enrolled in this course"
#         )

#     result = foundry_service.execute_course_enrollment_action(
#         course_id=course_id,
#         user_id=str(current_user.id)
#     )
#     if not result or result.get("status") == "error":
#         raise HTTPException(status_code=500, detail=result.get("message", "Enrollment failed"))
#     return result


# @router.get("/{course_id}/modules", status_code=status.HTTP_200_OK)
# def get_course_modules(
#     course_id: str,
#     current_user: User = Depends(get_current_user),
# ):
#     """List modules for a course. (1 module for now, more later)."""
#     status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
#     if not status_check.get("isEnrolled"):
#         raise HTTPException(status_code=403, detail="You must be enrolled to view modules")

#     return foundry_service.get_course_modules(course_id=course_id)


# @router.get("/{course_id}/modules/{module_id}/content", status_code=status.HTTP_200_OK)
# def get_module_content(
#     course_id: str,
#     module_id: str,
#     current_user: User = Depends(get_current_user),
# ):
#     """Get module content (video + PDF). Enrolled users only."""
#     status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
#     if not status_check.get("isEnrolled"):
#         raise HTTPException(status_code=403, detail="You must be enrolled to access content")

#     content = foundry_service.get_module_content(course_id=course_id, module_id=module_id)
#     if not content:
#         raise HTTPException(status_code=404, detail="Module content not found")
#     return content


# @router.get("/{course_id}/modules/{module_id}/quiz", status_code=status.HTTP_200_OK)
# def get_module_quiz(
#     course_id: str,
#     module_id: str,
#     current_user: User = Depends(get_current_user),
# ):
#     """Get quiz questions for a module. Enrolled users only."""
#     status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
#     if not status_check.get("isEnrolled"):
#         raise HTTPException(status_code=403, detail="You must be enrolled to access the quiz")

#     return foundry_service.get_course_quiz(course_id=course_id, module_id=module_id)


# @router.post("/{course_id}/modules/{module_id}/quiz/submit", status_code=status.HTTP_200_OK)
# def submit_module_quiz(
#     course_id: str,
#     module_id: str,
#     payload: TestSubmissionRequest,
#     current_user: User = Depends(get_current_user),
# ):
#     """Submit quiz answers. Auto-graded. If passed → module/course marked complete."""
#     status_check = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))
#     if not status_check.get("isEnrolled"):
#         raise HTTPException(status_code=403, detail="You must be enrolled to submit the quiz")

#     return foundry_service.grade_and_complete_course(
#         course_id=course_id,
#         module_id=module_id,
#         user_id=str(current_user.id),
#         submission_data=payload
#     )


# @router.get("/{course_id}/progress", status_code=status.HTTP_200_OK)
# def get_course_progress(
#     course_id: str,
#     current_user: User = Depends(get_current_user),
# ):
#     """Get enrollment status and completion info for a course."""
#     return foundry_service.get_course_progress(course_id=course_id, user_id=str(current_user.id))


from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from typing import Optional

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


@router.get("/", status_code=status.HTTP_200_OK)
def list_courses(
    offset: int = 0,
    limit: int = 6,
    category: Optional[str] = None,
    level: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """List all available courses."""
    try:
        result = foundry_service.get_all_courses(offset=offset, limit=limit, category=category, level=level)

        courses = []
        for c in result.get("courses", []):
            courses.append({
                "id": str(c.get("course_id", c.get("id", ""))),
                "title": c.get("title") or c.get("course_name1", "Untitled"),
                "tag": c.get("tag", "General"),
                "duration": c.get("duration1", "Self-paced"),
                "instructor": c.get("instructor", "ItsYar Team"),
                "description": c.get("description", ""),
                "image": c.get("image", ""),
                "badge": c.get("badge"),
                "level": c.get("level", "Beginner"),
                "enrolled": False,
            })

        return {"success": True, "courses": courses, "total": result.get("total", 0), "offset": offset, "limit": limit}

    except Exception as e:
        return error_response(500, f"Failed to fetch courses: {str(e)}")


@router.get("/search", status_code=status.HTTP_200_OK)
def search_courses(
    q: str = Query(..., min_length=2),
    limit: int = 10,
    current_user: User = Depends(get_current_user),
):
    """Search courses by keyword."""
    try:
        result = foundry_service.search_courses_catalog(query_str=q, limit=limit)
        return {"success": True, **result}
    except Exception as e:
        return error_response(500, f"Search failed: {str(e)}")


@router.get("/my", status_code=status.HTTP_200_OK)
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


@router.get("/{course_id}", status_code=status.HTTP_200_OK)
def get_course_details(
    course_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get single course details including enrollment status."""
    try:
        course = foundry_service.get_single_course(course_id=course_id)
        if not course:
            return error_response(404, "Course resource not found")

        enrollment = foundry_service.check_user_enrollment(course_id=course_id, user_id=str(current_user.id))

        # Build curriculum from content data
        content = foundry_service.get_module_content(course_id=course_id, module_id=course_id)

        return {
            "success": True,
            "data": {
                "id": str(course.get("course_id", course_id)),
                "title": course.get("title") or course.get("course_name1", ""),
                "tag": course.get("tag", "General"),
                "category": course.get("tag", "DEVELOPMENT"),
                "description": course.get("description", ""),
                "longDescription": course.get("about_the_course"),
                "level": course.get("level", "Beginner"),
                "modulesCount": 1,
                "duration": course.get("duration1", "Self-paced"),
                "thumbnail": course.get("image", ""),
                "instructor": course.get("instructor", "ItsYar Team"),
                #"videoUrl": course.get("course_url1"),
                #"pdfResource": course.get("derived") or course.get("course_resources1"),
                #"contentId": course.get("content_id"),
                "courseResource": course.get("course_resources1"),
                "curriculum": content,
                "takeaways": course.get("takeaways"),
                "isEnrolled": enrollment.get("isEnrolled", False),
            }
        }

    except Exception as e:
        return error_response(500, f"Failed to fetch course: {str(e)}")


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


@router.get("/{course_id}/modules", status_code=status.HTTP_200_OK)
def get_course_modules(
    course_id: str,
    current_user: User = Depends(get_current_user),
):
    """List modules for a course."""
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

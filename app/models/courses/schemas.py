from pydantic import BaseModel
from typing import Optional

class CourseSchema(BaseModel):
    courseId: str          # Maps to "Courses ID"
    courseName: str        # Maps to "Courses Name"
    courseResources: str   # Maps to "Courses Resources"
    courseUrl: str         # Maps to "course url"

    class Config:
        from_attributes = True
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TaskSchema(BaseModel):
    name: str              # Maps to "Name"
    taskId: str            # Maps to "Task ID"
    difficulty: str        # Maps to "difficulty"
    createdAt: datetime    # Maps to "Created At"
    createdBy: str         # Maps to "Created By"
    description: str       # Maps to "Description"
    estimationHours: float # Maps to "Estimation Hours"
    instructorId: str      # Maps to "Instructor ID"

    class Config:
        from_attributes = True
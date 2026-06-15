from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EventSchema(BaseModel):
    id: str
    title: str
    description: Optional[str] = ""
    status: str
    startDate: datetime
    endDate: datetime
    eventType: str
    orgId: str
    createdAt: datetime    # Maps to "Created At"
    createdBy: str         # Maps to "Created By"
    judgeUserId: str       # Maps to "Judge User id"

    class Config:
        from_attributes = True
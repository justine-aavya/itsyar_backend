# schemas.py
# Pure object schema tracking file. Left empty intentionally.

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class HackathonRegistrationRequest(BaseModel):
    full_name: str = Field(alias="fullName")
    email: str
    role: Optional[str] = "Participant"
    team_id: Optional[str] = Field(default=None, alias="teamId")
    agree_to_rules: bool = Field(default=False, alias="agreeToRules")
    consent_to_organizers: bool = Field(default=False, alias="consentToOrganizers")

    model_config = ConfigDict(populate_by_name=True)

class SubmissionRequest(BaseModel):
    language: str
    code: str
    notes: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


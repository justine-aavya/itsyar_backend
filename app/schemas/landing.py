from pydantic import BaseModel
from typing import List, Optional

# --- Metrics Schemas ---
class MetricsResponse(BaseModel):
    developersSkilled: str
    industryExperts: str
    skillImprovementRate: str
    placementMultiplier: str

# --- Content Schemas ---
class CourseItem(BaseModel):
    id: int
    name: str

class HackathonItem(BaseModel):
    id: int
    title: str
    date: str
    registrations: str

class ContentResponse(BaseModel):
    courses: List[CourseItem]
    hackathons: List[HackathonItem]
    categories: List[str]

# --- Reviews Schemas ---
class ReviewItem(BaseModel):
    name: str
    role: str
    text: str

# --- Leaderboard Schemas ---
class LeaderboardItem(BaseModel):
    rank: int
    name: str
    pts: Optional[str] = None

class LeaderboardResponse(BaseModel):
    leaderboard: List[LeaderboardItem]
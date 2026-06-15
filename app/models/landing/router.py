from fastapi import APIRouter, status, HTTPException
from app.integrations.palantir import foundry_service
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# Inline embedded schemas for easy consumption
class MetricsResponse(BaseModel):
    developersSkilled: str
    industryExperts: str
    skillImprovementRate: str
    placementMultiplier: str

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

class ReviewItem(BaseModel):
    name: str
    role: str
    text: str

class LeaderboardItem(BaseModel):
    rank: int
    name: str
    points: Optional[str] = None

class LeaderboardResponse(BaseModel):
    leaderboard: List[LeaderboardItem]

@router.get("/metrics", response_model=MetricsResponse)
def get_landing_metrics():
    return {
        "developersSkilled": "25K+",
        "industryExperts": "12K+",
        "skillImprovementRate": "70%",
        "placementMultiplier": "3x"
    }

@router.get("/content", response_model=ContentResponse)
def get_landing_content():
    try:
        raw_events = foundry_service.get_all_events()
        raw_tracks = foundry_service.get_all_tracks()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Failed to load content: {str(e)}")

    formatted_courses = [
        CourseItem(id=idx + 1, name=track.get("name") or track.get("title") or "Unnamed Track") 
        for idx, track in enumerate(raw_tracks[:2])
    ]

    formatted_hackathons = []
    for idx, event in enumerate(raw_events[:2]):
        title = event.get("title") or event.get("name") or "Untitled Event"
        start = event.get("startDate") or event.get("start_date") or "TBD"
        end = event.get("endDate") or event.get("end_date") or "TBD"
        clean_start = str(start).split("T")[0]
        clean_end = str(end).split("T")[0]
        
        reg_count = event.get("registered_count") or event.get("registrations") or 0
        try:
            reg_val = int(reg_count)
            reg_display = f"{reg_val}K+" if reg_val > 1 else str(reg_val)
        except (ValueError, TypeError):
            reg_display = str(reg_count)

        formatted_hackathons.append(
            HackathonItem(id=idx + 1, title=title, date=f"{clean_start} - {clean_end}", registrations=reg_display)
        )

    return ContentResponse(
        courses=formatted_courses,
        hackathons=formatted_hackathons,
        categories=["Cloud & DevOps", "AI / Machine Learning", "Web3", "Data Science"]
    )

@router.get("/reviews", response_model=List[ReviewItem])
def get_landing_reviews():
    return foundry_service.get_all_reviews()

@router.get("/leaderboards", response_model=LeaderboardResponse)
def get_landing_leaderboard():
    raw_leaderboard = foundry_service.get_top_leaderboard(limit=4)
    formatted_leaderboard = [
        LeaderboardItem(
            rank=item.get("rank") or (idx + 1),
            name=item.get("name") or "Anonymous User",
            pts=item.get("pts")
        ) for idx, item in enumerate(raw_leaderboard)
    ]
    return LeaderboardResponse(leaderboard=formatted_leaderboard)

# # landing.py
# from typing import List

# from fastapi import APIRouter, HTTPException
# from app.integrations.palantir import foundry_service
# from app.schemas.landing import (
#     MetricsResponse,
#     ContentResponse,
#     ReviewItem,
#     LeaderboardResponse,
#     CourseItem,
#     HackathonItem,
#     LeaderboardItem,
# )

# router = APIRouter()


# @router.get("/metrics", response_model=MetricsResponse)
# def get_landing_metrics():
#     """Fetches static marketing and promotional metrics to build the hero counters."""
#     return {
#         "developersSkilled": "25K+",
#         "industryExperts": "12K+",
#         "skillImprovementRate": "70%",
#         "placementMultiplier": "3x",
#     }


# @router.get("/content", response_model=ContentResponse)
# def get_landing_content():
#     """Fetches core course modules and upcoming hackathon data sets."""
#     try:
#         raw_events = foundry_service.get_all_events()
#         raw_tracks = foundry_service.get_all_tracks()
#     except Exception as e:
#         raise HTTPException(status_code=503, detail=f"Failed to load content: {str(e)}")

#     formatted_courses = [
#         CourseItem(
#             id=idx + 1,
#             name=track.get("name") or track.get("title") or "Unnamed Track",
#         )
#         for idx, track in enumerate(raw_tracks[:2])
#     ]

#     formatted_hackathons = []
#     for idx, event in enumerate(raw_events[:2]):
#         title = event.get("title") or event.get("name") or "Untitled Event"
#         start = event.get("startDate") or event.get("start_date") or "TBD"
#         end = event.get("endDate") or event.get("end_date") or "TBD"

#         clean_start = str(start).split("T")[0]
#         clean_end = str(end).split("T")[0]

#         reg_count = event.get("registered_count") or event.get("registrations") or 0
#         try:
#             reg_val = int(reg_count)
#             reg_display = f"{reg_val}K+" if reg_val > 1 else str(reg_val)
#         except (ValueError, TypeError):
#             reg_display = str(reg_count)

#         formatted_hackathons.append(
#             HackathonItem(
#                 id=idx + 1,
#                 title=title,
#                 date=f"{clean_start} - {clean_end}",
#                 registrations=reg_display,
#             )
#         )

#     static_categories = ["Cloud & DevOps", "AI / Machine Learning", "Web3", "Data Science"]

#     return ContentResponse(
#         courses=formatted_courses,
#         hackathons=formatted_hackathons,
#         categories=static_categories,
#     )


# @router.get("/reviews", response_model=List[ReviewItem])
# def get_landing_reviews():
#     """Fetches user reviews from the Ontology."""
#     return foundry_service.get_all_reviews()


# @router.get("/leaderboards", response_model=LeaderboardResponse)
# def get_landing_leaderboard():
#     """Fetches top leaderboard entries."""
#     raw_leaderboard = foundry_service.get_top_leaderboard(limit=4)

#     formatted_leaderboard = [
#         LeaderboardItem(
#             rank=item.get("rank") or (idx + 1),
#             name=item.get("name") or "Anonymous User",
#             pts=item.get("pts"),
#         )
#         for idx, item in enumerate(raw_leaderboard)
#     ]
#     return LeaderboardResponse(leaderboard=formatted_leaderboard)



from fastapi import APIRouter, status, HTTPException

from app.integrations.palantir import foundry_service

from typing import List



from app.schemas.landing import (

    MetricsResponse,

    ContentResponse,

    ReviewItem,

    LeaderboardResponse,

    CourseItem,

    HackathonItem,

    LeaderboardItem

)



router = APIRouter(prefix="/landing", tags=["Public Landing Page"])



# ─────────────────────────────────────────────

# GET /api/landing/metrics

# ─────────────────────────────────────────────

@router.get("/metrics", response_model=MetricsResponse)

def get_landing_metrics():

    """

    Fetches static marketing and promotional metrics to build the hero counters.

    No database overhead or authentication required.

    """

    return {

        "developersSkilled": "25K+",

        "industryExperts": "12K+",

        "skillImprovementRate": "70%",

        "placementMultiplier": "3x"

    }



# ─────────────────────────────────────────────

# GET /api/landing/content

# ─────────────────────────────────────────────

@router.get("/content", response_model=ContentResponse)

def get_landing_content():

    """Fetches core course modules and upcoming hackathon data sets."""

    try:

        # Pull records directly through the multi-mode service architecture

        raw_events = foundry_service.get_all_events()

        raw_tracks = foundry_service.get_all_tracks()

    except Exception as e:

        raise HTTPException(status_code=503, detail=f"Failed to load content: {str(e)}")



    # Format tracks into landing-page courses

    formatted_courses = [

        CourseItem(

            id=idx + 1,

            name=track.get("name") or track.get("title") or "Unnamed Track"

        )

        for idx, track in enumerate(raw_tracks[:2]) # Just grab the first two for landing display

    ]



    # Map your unified structure directly to the landing template properties safely

    formatted_hackathons = []

    for idx, event in enumerate(raw_events[:2]):

        # Fallback fields matching both local mock definitions and OSDK maps

        title = event.get("title") or event.get("name") or "Untitled Event"

       

        start = event.get("startDate") or event.get("start_date") or "TBD"

        end = event.get("endDate") or event.get("end_date") or "TBD"

       

        # Strip trailing timestamps out of ISO strings if they are too long for a small card

        clean_start = str(start).split("T")[0]

        clean_end = str(end).split("T")[0]

       

        # Safe extraction for registration metrics

        reg_count = event.get("registered_count") or event.get("registrations") or 0

        try:

            reg_val = int(reg_count)

            reg_display = f"{reg_val}K+" if reg_val > 1 else str(reg_val)

        except (ValueError, TypeError):

            reg_display = str(reg_count)



        formatted_hackathons.append(

            HackathonItem(

                id=idx + 1,

                title=title,

                date=f"{clean_start} - {clean_end}",

                registrations=reg_display

            )

        )



    static_categories = ["Cloud & DevOps", "AI / Machine Learning", "Web3", "Data Science"]



    return ContentResponse(

        courses=formatted_courses,

        hackathons=formatted_hackathons,

        categories=static_categories

    )



# ─────────────────────────────────────────────

# GET /api/landing/reviews

# ─────────────────────────────────────────────

@router.get("/reviews", response_model=List[ReviewItem])

def get_landing_reviews():

    return foundry_service.get_all_reviews()



# ─────────────────────────────────────────────

# GET /api/landing/leaderboards

# ─────────────────────────────────────────────

@router.get("/leaderboards", response_model=LeaderboardResponse)

def get_landing_leaderboard():

    raw_leaderboard = foundry_service.get_top_leaderboard(limit=4)

   

    formatted_leaderboard = [

        LeaderboardItem(

            rank=item.get("rank") or (idx + 1),

            name=item.get("name") or "Anonymous User",

            pts=item.get("pts") # Gracefully maps even if pts string is omitted

        ) for idx, item in enumerate(raw_leaderboard)

    ]

    return LeaderboardResponse(leaderboard=formatted_leaderboard) 


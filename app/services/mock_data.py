"""
Mock data that simulates Foundry Ontology objects.
Used when Foundry is not configured (FOUNDRY_URL is empty in .env).
"""

MOCK_EVENTS = [
    {
        "id": "evt-001",
        "name": "Vanyar Hackathon — Foundry Sprint I",
        "description": "Build innovative solutions using Palantir Foundry",
        "start_date": "2025-06-20",
        "end_date": "2025-06-22",
        "status": "active",
        "max_participants": 4,
        "registered_count": 3,
        "location": "Virtual",
    },
    {
        "id": "evt-002",
        "name": "AI & ML Challenge 2025",
        "description": "Solve real-world problems using AIP and machine learning",
        "start_date": "2025-07-15",
        "end_date": "2025-07-17",
        "status": "upcoming",
        "max_participants": 4,
        "registered_count": 1,
        "location": "Virtual",
    },
    {
        "id": "evt-003",
        "name": "Data Pipeline Showdown",
        "description": "Fastest and cleanest data pipeline wins",
        "start_date": "2025-05-01",
        "end_date": "2025-05-03",
        "status": "completed",
        "max_participants": 4,
        "registered_count": 4,
        "location": "Virtual",
    },
]

MOCK_TRACKS = [
    {
        "id": "trk-001",
        "name": "AIP & Agent Engineering",
        "description": "Build AI agents using Palantir AIP",
        "difficulty": "Advanced",
        "duration_hours": 32,
        "modules_count": 8,
        "enrolled_count": 142,
    },
    {
        "id": "trk-002",
        "name": "Pipeline Builder Fundamentals",
        "description": "No-code data transformation pipelines",
        "difficulty": "Beginner",
        "duration_hours": 16,
        "modules_count": 5,
        "enrolled_count": 289,
    },
    {
        "id": "trk-003",
        "name": "OSDK & Application Development",
        "description": "Build external applications with Foundry OSDK",
        "difficulty": "Intermediate",
        "duration_hours": 24,
        "modules_count": 6,
        "enrolled_count": 98,
    },
    {
        "id": "trk-004",
        "name": "Ontology Design Patterns",
        "description": "Model real-world concepts in the Foundry Ontology",
        "difficulty": "Intermediate",
        "duration_hours": 20,
        "modules_count": 5,
        "enrolled_count": 156,
    },
]

MOCK_CHALLENGES = {
    "evt-001": [
        {
            "id": "ch-001",
            "title": "Supply Chain Optimisation",
            "description": "Optimise delivery routes using Foundry pipelines",
            "scoring_type": "automatic",
            "max_score": 100,
            "difficulty": "Hard",
        },
        {
            "id": "ch-002",
            "title": "Customer Segmentation",
            "description": "Build an ontology-driven customer segmentation model",
            "scoring_type": "automatic",
            "max_score": 100,
            "difficulty": "Medium",
        },
        {
            "id": "ch-003",
            "title": "Real-time Dashboard",
            "description": "Create a live monitoring dashboard in Workshop",
            "scoring_type": "manual",
            "max_score": 100,
            "difficulty": "Medium",
        },
    ],
    "evt-002": [
        {
            "id": "ch-004",
            "title": "Fraud Detection Model",
            "description": "Build and deploy a fraud detection model using AIP",
            "scoring_type": "automatic",
            "max_score": 100,
            "difficulty": "Hard",
        },
        {
            "id": "ch-005",
            "title": "Sentiment Analysis Pipeline",
            "description": "Analyse customer feedback using LLM functions",
            "scoring_type": "automatic",
            "max_score": 100,
            "difficulty": "Medium",
        },
    ],
    "evt-003": [
        {
            "id": "ch-006",
            "title": "ETL Speed Challenge",
            "description": "Build the fastest data pipeline for 10M rows",
            "scoring_type": "automatic",
            "max_score": 100,
            "difficulty": "Hard",
        },
    ],
}

MOCK_STATS = {
    "total_users": 142,
    "active_events": 2,
    "completed_events": 1,
    "total_tracks": 4,
    "total_challenges": 6,
}


# ... Keep your existing MOCK_EVENTS, MOCK_TRACKS, MOCK_CHALLENGES, MOCK_STATS exactly as they are

MOCK_REVIEWS = [
    {
        "name": "Sarah K.",
        "role": "Software Engineer",
        "text": '"Won my first hackathon after just 2 weeks of learning. The format of platform is amazing!"'
    },
    {
        "name": "James T.",
        "role": "Full Stack Developer",
        "text": '"Best platform for sharpening skills before interviews and real-world projects."'
    }
]

MOCK_LEADERBOARD = [
    {"rank": 1, "name": "@nitish_dev", "pts": "5,840 pts", "score_num": 5840},
    {"rank": 2, "name": "@code_queen", "pts": "5,120 pts", "score_num": 5120},
    {"rank": 3, "name": "@build_master", "pts": "4,900 pts", "score_num": 4900},
    {"rank": 4, "name": "@hackpro89", "pts": "4,210 pts", "score_num": 4210},
    {"rank": 5, "name": "@algo_wizard", "pts": "3,800 pts", "score_num": 3800}
]
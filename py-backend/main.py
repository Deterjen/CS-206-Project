from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# University recommendation endpoint
@app.get("/api/recommendations")
async def get_recommendations():
    # This is a placeholder - replace with actual data from your database
    return {
        "universities": [
            {
                "id": "1",
                "name": "Singapore Management University",
                "location": "Singapore",
                "logo": "/placeholder.svg",
                "matchScore": 95,
                "images": [
                    "/placeholder.svg?height=400&width=600",
                    "/placeholder.svg?height=400&width=600",
                    "/placeholder.svg?height=400&width=600",
                ],
                "benefits": [
                    "Located in the city",
                    "Offers many scholarships",
                    "Strong industry connections",
                ],
                "drawbacks": [
                    "Highly competitive",
                    "Higher living costs",
                    "Intensive course load",
                ],
                "suitabilityReasons": [
                    "Located in the city",
                    "Offers many scholarships",
                    "Strong academic programs",
                ],
            },
            {
                "id": "2",
                "name": "National University of Singapore",
                "location": "Singapore",
                "logo": "/placeholder.svg",
                "matchScore": 92,
                "images": [
                    "/placeholder.svg?height=400&width=600",
                    "/placeholder.svg?height=400&width=600",
                    "/placeholder.svg?height=400&width=600",
                ],
                "benefits": [
                    "World-renowned research facilities",
                    "Comprehensive course offerings",
                    "Strong global partnerships",
                ],
                "drawbacks": [
                    "Large class sizes",
                    "Competitive academic environment",
                    "Campus is far from city center",
                ],
                "suitabilityReasons": [
                    "Matches your research interests",
                    "Aligns with your career goals",
                    "Strong academic reputation",
                ],
            },
            {
                "id": "3",
                "name": "Nanyang Technological University",
                "location": "Singapore",
                "logo": "/placeholder.svg",
                "matchScore": 88,
                "images": [
                    "/placeholder.svg?height=400&width=600",
                    "/placeholder.svg?height=400&width=600",
                    "/placeholder.svg?height=400&width=600",
                ],
                "benefits": [
                    "Modern campus facilities",
                    "Strong STEM programs",
                    "Active student life",
                ],
                "drawbacks": [
                    "Distance from city center",
                    "Limited parking",
                    "Less industry networking events",
                ],
                "suitabilityReasons": [
                    "Matches your interest in technology",
                    "Offers your preferred course specializations",
                    "Good research opportunities",
                ],
            },
            {
                "id": "4",
                "name": "Singapore Institute of Technology",
                "location": "Singapore",
                "logo": "/placeholder.svg",
                "matchScore": 85,
                "images": [
                    "/placeholder.svg?height=400&width=600",
                    "/placeholder.svg?height=400&width=600",
                    "/placeholder.svg?height=400&width=600",
                ],
                "benefits": [
                    "Industry-focused curriculum",
                    "Small class sizes",
                    "Applied learning approach",
                ],
                "drawbacks": [
                    "Newer institution",
                    "Limited campus facilities",
                    "Fewer research opportunities",
                ],
                "suitabilityReasons": [
                    "Practical learning style matches your preference",
                    "Industry connections align with your goals",
                    "Smaller community atmosphere",
                ],
            },
            {
                "id": "5",
                "name": "Singapore University of Technology and Design",
                "location": "Singapore",
                "logo": "/placeholder.svg",
                "matchScore": 82,
                "images": [
                    "/placeholder.svg?height=400&width=600",
                    "/placeholder.svg?height=400&width=600",
                    "/placeholder.svg?height=400&width=600",
                ],
                "benefits": [
                    "Innovative teaching methods",
                    "Design-centric education",
                    "Strong industry projects",
                ],
                "drawbacks": [
                    "Limited course options",
                    "Specific teaching style",
                    "Smaller alumni network",
                ],
                "suitabilityReasons": [
                    "Innovative approach matches your learning style",
                    "Project-based learning preference",
                    "Technology focus aligns with your interests",
                ],
            },
        ]
    }

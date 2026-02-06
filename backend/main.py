from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List

app = FastAPI(title="VisionWire LMS", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Course(BaseModel):
    id: int
    title: str
    instructor: str
    duration: str
    enrolled: int
    rating: float

courses = [
    Course(id=1, title="Introduction to Python", instructor="Dr. Smith", duration="6 weeks", enrolled=1250, rating=4.8),
    Course(id=2, title="Web Development Bootcamp", instructor="Prof. Johnson", duration="12 weeks", enrolled=2100, rating=4.9),
    Course(id=3, title="Data Science Fundamentals", instructor="Dr. Lee", duration="8 weeks", enrolled=1850, rating=4.7),
    Course(id=4, title="Machine Learning A-Z", instructor="Prof. Brown", duration="10 weeks", enrolled=3200, rating=4.9),
]

@app.get("/")
async def root():
    return {
        "message": "VisionWire LMS API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/courses")
async def get_courses():
    return {"courses": courses, "total": len(courses)}

@app.get("/courses/{course_id}")
async def get_course(course_id: int):
    course = next((c for c in courses if c.id == course_id), None)
    if not course:
        return {"error": "Course not found"}
    return course

@app.get("/stats")
async def get_stats():
    return {
        "totalCourses": len(courses),
        "totalStudents": sum(c.enrolled for c in courses),
        "averageRating": sum(c.rating for c in courses) / len(courses),
        "activeInstructors": len(set(c.instructor for c in courses))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
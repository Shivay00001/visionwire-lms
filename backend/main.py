"""VisionWire LMS API — course CRUD backed by SQLite.

Wave-1 fix (2026-09-24): replaced the hardcoded in-memory course list with a
real SQLite-backed store (stdlib sqlite3, no extra dependencies). On first
start the database is seeded from backend/data/courses_seed.json; afterwards
all creates/updates/deletes persist in lms.db.
"""
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "lms.db"
SEED_PATH = BASE_DIR / "data" / "courses_seed.json"

app = FastAPI(title="VisionWire LMS", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CourseBase(BaseModel):
    title: str
    instructor: str
    duration: str
    enrolled: int = 0
    rating: float = 0.0


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    instructor: Optional[str] = None
    duration: Optional[str] = None
    enrolled: Optional[int] = None
    rating: Optional[float] = None


class Course(CourseBase):
    id: int


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS courses (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   title TEXT NOT NULL,
                   instructor TEXT NOT NULL,
                   duration TEXT NOT NULL,
                   enrolled INTEGER NOT NULL DEFAULT 0,
                   rating REAL NOT NULL DEFAULT 0.0
               )"""
        )
        count = conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
        if count == 0 and SEED_PATH.exists():
            seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))
            conn.executemany(
                "INSERT INTO courses (title, instructor, duration, enrolled, rating)"
                " VALUES (?, ?, ?, ?, ?)",
                [(c["title"], c["instructor"], c["duration"],
                  c.get("enrolled", 0), c.get("rating", 0.0)) for c in seed],
            )


init_db()


def row_to_course(row) -> Course:
    return Course(id=row["id"], title=row["title"], instructor=row["instructor"],
                  duration=row["duration"], enrolled=row["enrolled"], rating=row["rating"])


@app.get("/")
async def root():
    return {"message": "VisionWire LMS API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/courses")
async def list_courses():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM courses ORDER BY id").fetchall()
    courses = [row_to_course(r) for r in rows]
    return {"courses": courses, "total": len(courses)}


@app.post("/courses", status_code=201)
async def create_course(course: CourseCreate):
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO courses (title, instructor, duration, enrolled, rating)"
            " VALUES (?, ?, ?, ?, ?)",
            (course.title, course.instructor, course.duration, course.enrolled, course.rating),
        )
        new_id = cur.lastrowid
        row = conn.execute("SELECT * FROM courses WHERE id = ?", (new_id,)).fetchone()
    return row_to_course(row)


@app.get("/courses/{course_id}")
async def get_course(course_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Course not found")
    return row_to_course(row)


@app.put("/courses/{course_id}")
async def update_course(course_id: int, patch: CourseUpdate):
    updates = {k: v for k, v in patch.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    with get_db() as conn:
        if not conn.execute("SELECT 1 FROM courses WHERE id = ?", (course_id,)).fetchone():
            raise HTTPException(status_code=404, detail="Course not found")
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        conn.execute(f"UPDATE courses SET {set_clause} WHERE id = ?",
                     (*updates.values(), course_id))
        row = conn.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
    return row_to_course(row)


@app.delete("/courses/{course_id}")
async def delete_course(course_id: int):
    with get_db() as conn:
        cur = conn.execute("DELETE FROM courses WHERE id = ?", (course_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Course not found")
    return {"deleted": course_id}


@app.get("/stats")
async def get_stats():
    with get_db() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS n, COALESCE(SUM(enrolled),0) AS students,"
            " COALESCE(AVG(rating),0) AS avg_rating,"
            " COUNT(DISTINCT instructor) AS instructors FROM courses"
        ).fetchone()
    return {
        "totalCourses": row["n"],
        "totalStudents": row["students"],
        "averageRating": round(row["avg_rating"], 2),
        "activeInstructors": row["instructors"],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)

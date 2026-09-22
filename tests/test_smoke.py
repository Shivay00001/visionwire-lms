"""Smoke test: backend modules parse; frontend entries exist."""
import ast
from pathlib import Path

ROOT = Path(__file__).parent.parent
BACKEND_MODULES = [
    "backend/main.py",
    "backend/config.py",
    "backend/api/auth.py",
    "backend/models/schema.py",
    "backend/services/llm_client.py",
    "backend/engines/assessment_engine.py",
    "backend/engines/content_engine.py",
    "backend/engines/curriculum_engine.py",
]


def test_backend_modules_parse():
    for rel in BACKEND_MODULES:
        p = ROOT / rel
        assert p.exists(), f"{rel} missing"
        ast.parse(p.read_text(encoding="utf-8"), filename=rel)


def test_frontend_entries_exist():
    assert (ROOT / "frontend" / "package.json").exists()
    assert (ROOT / "frontend" / "next.config.ts").exists()
    assert (ROOT / "frontend" / "components" / "student_dashboard.tsx").exists()
    assert (ROOT / "frontend" / "components" / "teacher_dashboard.tsx").exists()

from backend.app.services.normalize import (
    normalize_employment_type, normalize_locations, normalize_skills,
    normalize_work_mode, parse_date, parse_salary,
)


def test_skill_variants_become_one_name():
    skills, unknown = normalize_skills(
        ["ReactJS", "React.js", "react", "python3", "Node JS", "REST APIs", "Kubernetes"])
    assert skills == ["React", "Python", "Node.js", "REST API", "Kubernetes"]
    assert unknown == ["Kubernetes"]


def test_locations():
    assert normalize_locations("BLR / Chennai") == ["Bengaluru", "Chennai"]
    assert normalize_locations("Mohali, Punjab") == ["Mohali"]
    assert normalize_locations(None) == []


def test_salary():
    assert parse_salary("4-7 LPA") == (400000, 700000)
    assert parse_salary("3.5 LPA") == (350000, 350000)
    assert parse_salary("15k-20k per month") == (180000, 240000)
    assert parse_salary("up to 8 LPA") == (None, 800000)
    assert parse_salary("Not disclosed") == (None, None)


def test_dates():
    assert parse_date("17 Oct 2026") == "2026-10-17"
    assert parse_date("17th October, 2026") == "2026-10-17"
    assert parse_date("garbage") is None


def test_type_and_mode():
    assert normalize_employment_type("Full Time") == "Full-time"
    assert normalize_employment_type("Internship") == "Internship"
    assert normalize_work_mode("Work from home") == "Remote"
    assert normalize_work_mode("Hybrid") == "Hybrid"
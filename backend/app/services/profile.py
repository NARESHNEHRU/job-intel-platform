import copy
from datetime import datetime, timezone

from backend.app.db.mongo import db
from backend.app.services.normalize import (
    normalize_locations, normalize_skills, normalize_work_mode,
)

profiles = db["profiles"]
USER_ID = "me"          # no login yet: one local user

EMPTY = {
    "name": "", "skills": [], "experience_years": 0, "education": "",
    "preferred_roles": "", "preferred_locations": [],
    "min_salary_lpa": None, "work_mode": None,
}


def load_profile() -> dict:
    doc = profiles.find_one({"_id": USER_ID}) or {}
    profile = copy.deepcopy(EMPTY)
    profile.update({k: doc[k] for k in EMPTY if k in doc})
    return profile


def save_profile(data: dict) -> dict:
    skills, _ = normalize_skills(data.get("skills"))
    locations = []
    for loc in data.get("preferred_locations") or []:
        for city in normalize_locations(loc):
            if city not in locations:
                locations.append(city)
    clean = {
        "name": (data.get("name") or "").strip(),
        "skills": skills,
        "experience_years": data.get("experience_years") or 0,
        "education": (data.get("education") or "").strip(),
        "preferred_roles": (data.get("preferred_roles") or "").strip(),
        "preferred_locations": locations,
        "min_salary_lpa": data.get("min_salary_lpa"),
        "work_mode": normalize_work_mode(data.get("work_mode")),
    }
    profiles.update_one(
        {"_id": USER_ID},
        {"$set": {**clean, "updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    return clean
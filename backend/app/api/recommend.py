from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Query

from backend.app.db.mongo import db
from backend.app.services.profile import load_profile
from backend.app.services.recommend import (
    match_job, profile_ready, profile_to_text, recommend, semantic_scores,
)

router = APIRouter(tags=["recommendations"])


@router.get("/recommendations")
def recommendations(limit: int = Query(10, ge=1, le=50)):
    p = load_profile()
    if not profile_ready(p):
        return {"has_profile": False, "items": []}
    return {"has_profile": True, "items": recommend(p, limit)}


@router.get("/jobs/{job_id}/match")
def job_match(job_id: str):
    p = load_profile()
    if not profile_ready(p):
        return {"has_profile": False}
    try:
        doc = db["jobs"].find_one({"_id": ObjectId(job_id)})
    except InvalidId:
        raise HTTPException(400, "Invalid job id")
    if not doc or not doc.get("normalized"):
        raise HTTPException(404, "Job not found")
    sim = semantic_scores(profile_to_text(p)).get(job_id)
    return {"has_profile": True, **match_job(p, doc, sim)}
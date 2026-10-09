from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException

from backend.app.db.mongo import db
from backend.app.services.profile import USER_ID
from backend.app.services.search import to_public


router = APIRouter(prefix="/saved", tags=["saved"])

saved = db["saved_jobs"]
jobs = db["jobs"]

saved.create_index(
    [("user_id", 1), ("job_id", 1)],
    unique=True,
)


def _oid(job_id: str) -> ObjectId:
    try:
        return ObjectId(job_id)
    except InvalidId:
        raise HTTPException(400, "Invalid job id")


@router.get("/ids")
def saved_ids():
    return [
        str(s["job_id"])
        for s in saved.find({"user_id": USER_ID})
    ]


@router.get("")
def saved_jobs():
    rows = list(
        saved.find({"user_id": USER_ID})
        .sort("saved_at", -1)
    )

    docs = {
        d["_id"]: d
        for d in jobs.find(
            {
                "_id": {
                    "$in": [r["job_id"] for r in rows]
                }
            }
        )
    }

    return {
        "items": [
            to_public(docs[r["job_id"]])
            for r in rows
            if r["job_id"] in docs
            and docs[r["job_id"]].get("normalized")
        ]
    }


@router.post("/{job_id}")
def save_job(job_id: str):
    oid = _oid(job_id)

    if not jobs.find_one({"_id": oid}, {"_id": 1}):
        raise HTTPException(404, "Job not found")

    saved.update_one(
        {"user_id": USER_ID, "job_id": oid},
        {
            "$setOnInsert": {
                "saved_at": datetime.now(timezone.utc)
            }
        },
        upsert=True,
    )

    return {"saved": True}


@router.delete("/{job_id}")
def unsave_job(job_id: str):
    saved.delete_one(
        {
            "user_id": USER_ID,
            "job_id": _oid(job_id),
        }
    )

    return {"saved": False}
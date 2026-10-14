import re
from datetime import date

from bson import ObjectId

from backend.app.db.mongo import db
from backend.app.db.vector_store import get_collection
from backend.app.services.embeddings import embed

jobs = db["jobs"]

PUBLIC_FIELDS = [
    "company", "job_title", "locations", "experience_min_years",
    "experience_max_years", "salary_text", "salary_min_inr", "salary_max_inr",
    "skills", "education", "employment_type", "work_mode",
    "walk_in_date", "walk_in_time", "venue", "application_deadline",
    "application_url", "contact",
]


def _ci(value: str):
    """case-insensitive exact match: 'python' matches 'Python'"""
    return re.compile(f"^{re.escape(value)}$", re.IGNORECASE)


def build_filter(location=None, skills=None, experience=None, fresher=False,
                 min_salary_lpa=None, work_mode=None, employment_type=None):
    today = date.today().isoformat()
    clauses = [
        {"status": "ready"},
        # hide walk-ins and deadlines that already passed
        {"$or": [{"normalized.walk_in_date": None},
                 {"normalized.walk_in_date": {"$gte": today}}]},
        {"$or": [{"normalized.application_deadline": None},
                 {"normalized.application_deadline": {"$gte": today}}]},
    ]
    if location:
        clauses.append({"normalized.locations": _ci(location)})
    for skill in skills or []:
        clauses.append({"normalized.skills": _ci(skill)})
    if fresher:
        experience = 0
    if experience is not None:
        clauses.append({"$or": [
            {"normalized.experience_min_years": None},
            {"normalized.experience_min_years": {"$lte": experience}},
        ]})
    if min_salary_lpa:
        clauses.append({
            "normalized.salary_max_inr": {
                "$gt": min_salary_lpa * 100_000
            }
        })
    if work_mode:
        clauses.append({"normalized.work_mode": work_mode})
    if employment_type:
        clauses.append({"normalized.employment_type": employment_type})
    return {"$and": clauses}


def to_public(doc, score=None):
    n = doc.get("normalized") or {}
    item = {
        "id": str(doc["_id"]),
        "source_chat": doc.get("source_chat"),
        "posted_at": doc.get("posted_at"),
        **{k: n.get(k) for k in PUBLIC_FIELDS},
    }
    if score is not None:
        item["score"] = round(score, 3)
    return item


def list_jobs(flt, page=1, limit=20):
    total = jobs.count_documents(flt)
    cursor = jobs.find(flt).sort("posted_at", -1).skip((page - 1) * limit).limit(limit)
    return {"total": total, "page": page, "items": [to_public(d) for d in cursor]}


def vector_search(text, flt, limit=10, candidates=100):
    """1) find the closest jobs by meaning  2) keep only those passing the filters"""
    col = get_collection()
    count = col.count()
    if count == 0:
        return []
    res = col.query(query_embeddings=[embed(text, "query")],
                    n_results=min(candidates, count))
    ids = res["ids"][0]
    scores = {i: 1 - d for i, d in zip(ids, res["distances"][0])}
    docs = {
        str(d["_id"]): d
        for d in jobs.find({"$and": [flt, {"_id": {"$in": [ObjectId(i) for i in ids]}}]})
    }
    ranked = [
    to_public(docs[i], scores[i])
    for i in ids
    if i in docs and scores[i] >= 0.55
    ]
    return ranked[:limit]
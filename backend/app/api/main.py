from backend.app.api import profile, saved, recommend, chat
from bson import ObjectId
from bson.errors import InvalidId

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


from backend.app.db.mongo import db

from backend.app.services.search import (
    build_filter,
    list_jobs,
    to_public,
    vector_search,
)

from backend.app.agent.query_understanding import understand_query


app = FastAPI(title="Job Intelligence API")


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Profile Router
# ---------------------------------------------------------

app.include_router(profile.router)
app.include_router(saved.router)
app.include_router(recommend.router)
app.include_router(chat.router)

jobs = db["jobs"]


# ---------------------------------------------------------
# Health
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "ready_jobs": jobs.count_documents(
            {"status": "ready"}
        ),
    }


# ---------------------------------------------------------
# List jobs
# ---------------------------------------------------------

@app.get("/jobs")
def get_jobs(
    location: str | None = None,
    skills: list[str] = Query(default=[]),
    experience: int | None = None,
    fresher: bool = False,
    min_salary_lpa: float | None = None,
    work_mode: str | None = None,
    employment_type: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
):
    flt = build_filter(
        location,
        skills,
        experience,
        fresher,
        min_salary_lpa,
        work_mode,
        employment_type,
    )

    return list_jobs(
        flt,
        page,
        limit,
    )


# ---------------------------------------------------------
# Get single job
# ---------------------------------------------------------

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    try:
        doc = jobs.find_one(
            {"_id": ObjectId(job_id)}
        )
    except InvalidId:
        raise HTTPException(
            400,
            "Invalid job id",
        )

    if not doc or not doc.get("normalized"):
        raise HTTPException(
            404,
            "Job not found",
        )

    item = to_public(doc)

    item["original_text"] = doc["input_text"]

    item["warnings"] = (
        doc.get("validation", {})
        .get("warnings", [])
    )

    return item


# ---------------------------------------------------------
# Filter metadata
# ---------------------------------------------------------

@app.get("/meta/filters")
def meta_filters():
    ready = {
        "status": "ready"
    }

    return {
        "locations": sorted(
            jobs.distinct(
                "normalized.locations",
                ready,
            )
        ),
        "skills": sorted(
            jobs.distinct(
                "normalized.skills",
                ready,
            )
        ),
    }


# ---------------------------------------------------------
# Semantic search
# ---------------------------------------------------------

@app.get("/search")
def search(
    q: str = Query(..., min_length=2),
    location: str | None = None,
    skills: list[str] = Query(default=[]),
    experience: int | None = None,
    fresher: bool = False,
    min_salary_lpa: float | None = None,
    work_mode: str | None = None,
    employment_type: str | None = None,
    limit: int = Query(10, ge=1, le=50),
):
    flt = build_filter(
        location,
        skills,
        experience,
        fresher,
        min_salary_lpa,
        work_mode,
        employment_type,
    )

    return {
        "query": q,
        "items": vector_search(
            q,
            flt,
            limit,
        ),
    }


# ---------------------------------------------------------
# AI natural-language search
# ---------------------------------------------------------

@app.get("/ask")
def ask(
    q: str = Query(..., min_length=2),
    location: str | None = None,
    fresher: bool = False,
    limit: int = Query(10, ge=1, le=50),
):
    f = understand_query(q)

    flt = build_filter(
        location=f["location"] or location,
        skills=f["skills"],
        fresher=f["fresher"] or fresher,
        min_salary_lpa=f["min_salary_lpa"],
        work_mode=f["work_mode"],
    )

    return {
        "understood": f,
        "items": vector_search(
            f["semantic_text"],
            flt,
            limit,
        ),
    }
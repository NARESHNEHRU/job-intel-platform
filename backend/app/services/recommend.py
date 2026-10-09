from backend.app.db.mongo import db
from backend.app.db.vector_store import get_collection
from backend.app.services.degrees import accepts_any, find_degrees
from backend.app.services.embeddings import embed
from backend.app.services.search import build_filter, to_public


jobs = db["jobs"]

WEIGHTS = {
    "skills": 0.40,
    "semantic": 0.25,
    "experience": 0.15,
    "location": 0.10,
    "education": 0.05,
    "salary": 0.05,
}


def profile_ready(p: dict) -> bool:
    return bool(p.get("skills") or p.get("preferred_roles"))


def profile_to_text(p: dict) -> str:
    parts = []

    if p.get("preferred_roles"):
        parts.append(
            f"Looking for: {p['preferred_roles']}"
        )

    if p.get("skills"):
        parts.append(
            "Skills: " + ", ".join(p["skills"])
        )

    if p.get("education"):
        parts.append(
            f"Education: {p['education']}"
        )

    return "\n".join(parts)


def semantic_scores(text: str) -> dict:
    col = get_collection()
    n = col.count()

    if not text or n == 0:
        return {}

    res = col.query(
        query_embeddings=[embed(text, "query")],
        n_results=n,
    )

    return {
        job_id: 1 - distance
        for job_id, distance in zip(
            res["ids"][0],
            res["distances"][0],
        )
    }


def match_job(
    profile: dict,
    doc: dict,
    sim=None,
) -> dict:

    n = doc["normalized"]

    scores = []
    reasons = []

    # -------------------------
    # Skills
    # -------------------------
    mine = {
        s.lower()
        for s in profile.get("skills", [])
    }

    job_skills = n.get("skills") or []

    matched = [
        s for s in job_skills
        if s.lower() in mine
    ]

    missing = [
        s for s in job_skills
        if s.lower() not in mine
    ]

    if job_skills and mine:
        scores.append(
            (
                "skills",
                len(matched) / len(job_skills),
            )
        )

        if matched:
            reasons.append(
                f"You have {len(matched)} of "
                f"{len(job_skills)} listed skills: "
                f"{', '.join(matched)}"
            )
        else:
            reasons.append(
                "None of the listed skills are "
                "in your profile yet"
            )

    # -------------------------
    # Semantic similarity
    # -------------------------
    if sim is not None:
        semantic_score = min(
            1.0,
            max(
                0.0,
                (sim - 0.35) / 0.40,
            ),
        )

        scores.append(
            ("semantic", semantic_score)
        )

        if semantic_score >= 0.6:
            reasons.append(
                "The role is close in meaning "
                "to what you are looking for"
            )

    # -------------------------
    # Experience
    # -------------------------
    exp = profile.get("experience_years")
    lo = n.get("experience_min_years")
    hi = n.get("experience_max_years")

    if exp is not None and lo is not None:
        gap = lo - exp

        if gap <= 0:
            experience_score = 1.0

            reasons.append(
                f"Your experience ({exp:g} yrs) "
                f"meets the minimum ({lo:g} yrs)"
            )

            if hi is not None and exp > hi:
                experience_score = 0.5

                reasons.append(
                    f"Note: the job targets up to "
                    f"{hi:g} years"
                )

        elif gap <= 1:
            experience_score = 0.5

            reasons.append(
                f"Slightly below the minimum "
                f"experience ({lo:g} yrs)"
            )

        else:
            experience_score = 0.0

            reasons.append(
                f"Needs {lo:g}+ years of experience"
            )

        scores.append(
            ("experience", experience_score)
        )

    # -------------------------
    # Location
    # -------------------------
    wanted = {
        l.lower()
        for l in profile.get(
            "preferred_locations",
            [],
        )
    }

    job_locs = [
        l.lower()
        for l in n.get("locations") or []
    ]

    if wanted and job_locs:
        if (
            wanted & set(job_locs)
            or "pan india" in job_locs
            or n.get("work_mode") == "Remote"
        ):
            location_score = 1.0

            reasons.append(
                "Location fits your preferences"
            )

        else:
            location_score = 0.0

            reasons.append(
                f"Located in "
                f"{', '.join(n['locations'])}, "
                "not your preferred cities"
            )

        scores.append(
            ("location", location_score)
        )

    # -------------------------
    # Education
    # -------------------------
    job_edu = n.get("education")
    my_degrees = find_degrees(
        profile.get("education")
    )

    if job_edu and my_degrees:

        if (
            accepts_any(job_edu)
            or (
                my_degrees
                & find_degrees(job_edu)
            )
        ):
            education_score = 1.0

            reasons.append(
                "Your education fits"
            )

        elif find_degrees(job_edu):
            education_score = 0.0

            reasons.append(
                f"Asks for: {job_edu}"
            )

        else:
            education_score = 0.0

        scores.append(
            ("education", education_score)
        )

    # -------------------------
    # Salary
    # -------------------------
    wanted_salary = profile.get(
        "min_salary_lpa"
    )

    top_salary = n.get(
        "salary_max_inr"
    )

    if wanted_salary and top_salary:

        salary_ok = (
            top_salary
            >= wanted_salary * 100_000
        )

        salary_score = (
            1.0
            if salary_ok
            else 0.0
        )

        scores.append(
            ("salary", salary_score)
        )

        reasons.append(
            "Salary meets your minimum"
            if salary_ok
            else "Salary is below your minimum"
        )

    # -------------------------
    # Final weighted score
    # -------------------------
    total = None

    if scores:
        weighted_sum = sum(
            WEIGHTS[key] * value
            for key, value in scores
        )

        total_weight = sum(
            WEIGHTS[key]
            for key, _ in scores
        )

        total = (
            weighted_sum
            / total_weight
        )

    return {
        "score": (
            round(total * 100)
            if total is not None
            else None
        ),
        "matched_skills": matched,
        "missing_skills": missing,
        "reasons": reasons,
        "breakdown": {
            key: round(value * 100)
            for key, value in scores
        },
    }


def recommend(
    profile: dict,
    limit: int = 10,
) -> list:

    sims = semantic_scores(
        profile_to_text(profile)
    )

    ranked = []

    for doc in jobs.find(
        build_filter()
    ).limit(500):

        match = match_job(
            profile,
            doc,
            sims.get(str(doc["_id"])),
        )

        if match["score"] is not None:
            ranked.append(
                (
                    match["score"],
                    doc,
                    match,
                )
            )

    ranked.sort(
        key=lambda x: x[0],
        reverse=True,
    )

    return [
        {
            **to_public(doc),
            "match": match,
        }
        for _, doc, match in ranked[:limit]
    ]
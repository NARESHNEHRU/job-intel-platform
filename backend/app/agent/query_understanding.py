import json
import os
import re

import ollama
from dotenv import load_dotenv

from backend.app.services.normalize import (
    normalize_locations,
    normalize_skills,
    normalize_work_mode,
)


load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")


SYSTEM = """You turn a job-seeker's question into search filters.

Return ONLY a JSON object with these keys:
search_text (short description of the role or topic, or null),
location (one city name, or null),
skills (list of skill names, [] if none),
fresher (true only if the user asks for fresher or entry-level jobs, else false),
min_salary_lpa (number, or null),
work_mode ("Remote", "Hybrid", "Onsite", or null).

Use ONLY what the user wrote.
Use null or [] when something is not mentioned.
Never invent anything."""


def understand_query(question: str) -> dict:

    # ---------------------------------------------------------
    # 1. Ask the local LLM to understand the question
    # ---------------------------------------------------------

    try:
        resp = ollama.chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM,
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
            format="json",
            options={"temperature": 0},
        )

        data = json.loads(
            resp["message"]["content"]
        )

        if not isinstance(data, dict):
            data = {}

    except Exception:
        data = {}

    q = question.lower()

    # ---------------------------------------------------------
    # 2. Normalize skills
    # ---------------------------------------------------------

    skills_all = (
        data.get("skills")
        if isinstance(data.get("skills"), list)
        else []
    )

    skills_all = [
        s
        for s in skills_all
        if isinstance(s, str)
    ]

    known, unknown = normalize_skills(
        skills_all
    )

    hard_skills = [
        s
        for s in known
        if s not in unknown
    ]

    # ---------------------------------------------------------
    # 3. Normalize location
    # ---------------------------------------------------------

    locations = (
        normalize_locations(
            data.get("location")
        )
        if isinstance(data.get("location"), str)
        else []
    )

    # ---------------------------------------------------------
    # 4. Extract salary directly from the question
    # ---------------------------------------------------------
    # Examples:
    # "above 5 LPA"       -> 5
    # "5.5 LPA"           -> 5.5
    # "salary 6 lakhs"    -> 6
    # "above 4 lakh"      -> 4
    #
    # This is intentionally deterministic instead of relying
    # only on the LLM.

    salary = None

    salary_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:lpa|lakhs?|lakh)",
        q,
        re.IGNORECASE,
    )

    if salary_match:
        salary = float(
            salary_match.group(1)
        )

    # ---------------------------------------------------------
    # 5. Detect fresher requirement
    # ---------------------------------------------------------

    fresher = (
        bool(data.get("fresher"))
        and any(
            word in q
            for word in (
                "fresher",
                "entry",
                "graduate",
                "no experience",
            )
        )
    )

    # ---------------------------------------------------------
    # 6. Build semantic search text
    # ---------------------------------------------------------

    search_text = (
        data.get("search_text")
        if isinstance(
            data.get("search_text"),
            str,
        )
        else ""
    )

    semantic = (
        " ".join(
            [search_text] + skills_all
        ).strip()
        or question
    )

    # ---------------------------------------------------------
    # 7. Return final filters
    # ---------------------------------------------------------

    return {
        "semantic_text": semantic,
        "location": (
            locations[0]
            if locations
            else None
        ),
        "skills": hard_skills,
        "fresher": fresher,
        "min_salary_lpa": salary,
        "work_mode": normalize_work_mode(
            data.get("work_mode")
        ),
    }
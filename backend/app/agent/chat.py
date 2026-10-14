import os
import re

import ollama
from bson import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv

from backend.app.agent.query_understanding import understand_query
from backend.app.db.mongo import db
from backend.app.services.profile import load_profile
from backend.app.services.recommend import (
    match_job, profile_ready, profile_to_text, recommend, semantic_scores,
)
from backend.app.services.search import build_filter, to_public, vector_search

load_dotenv()
MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
jobs = db["jobs"]

ORDINALS = {"first": 0, "1st": 0, "second": 1, "2nd": 1, "third": 2, "3rd": 2}


# ---------- STEP 1: what is the user asking? (plain code, no AI) ----------
def detect_intent(message: str) -> str:
    m = message.lower()
    if re.fullmatch(r"\W*(hi|hello|hey|thanks|thank you|ok|okay)\W*", m):
        return "smalltalk"
    if any(w in m for w in ("missing", "skill gap", "skills gap", "lack",
                            "need to learn", "should i learn", "what do i need")):
        return "gap"
    if any(w in m for w in ("my profile", "match me", "matches me", "for me",
                            "suit me", "recommend", "best jobs for")):
        return "matches"
    return "search"


def resolve_job_id(message, job_id, last_ids):
    """Which job does 'this job' / 'the first one' mean?"""
    if job_id:
        return job_id
    m = message.lower()
    for word, i in ORDINALS.items():
        if re.search(rf"\b{word}\b", m) and i < len(last_ids):
            return last_ids[i]
    if len(last_ids) == 1 and re.search(r"\b(this|that|it)\b", m):
        return last_ids[0]
    return None


# ---------- STEP 2: the AI writes a short intro (checked by code) ----------
SUMMARY_SYSTEM = """You are a friendly job-search assistant.
The user asked a question and our database returned the jobs listed below.
Write 1-2 short sentences that introduce the results.
Rules:
- Mention only facts that appear in the list.
- Do not list every job; the job cards are shown to the user separately.
- Never mention a job, company, salary or number that is not in the list."""


def _brief(items):
    lines = []
    for i, j in enumerate(items, 1):
        bits = [f"{j.get('job_title') or 'Untitled'} at {j.get('company') or 'unknown company'}"]
        if j.get("locations"):
            bits.append("in " + ", ".join(j["locations"]))
        if j.get("skills"):
            bits.append("skills: " + ", ".join(j["skills"][:6]))
        if j.get("match"):
            bits.append(f"{j['match']['score']}% match")
        lines.append(f"{i}. " + "; ".join(bits))
    return "\n".join(lines)


def summarize(question, items):
    first = items[0]
    fallback = (f"I found {len(items)} job(s). The closest is "
                f"{first.get('job_title') or 'a role'} at {first.get('company') or 'an unnamed company'}.")
    brief = _brief(items)
    try:
        resp = ollama.chat(
            model=MODEL,
            messages=[{"role": "system", "content": SUMMARY_SYSTEM},
                      {"role": "user", "content": f"Question: {question}\n\nJobs found:\n{brief}"}],
            options={"temperature": 0},
        )
        reply = resp["message"]["content"].strip()
    except Exception:
        return fallback
    # code double-check: every number in the reply must exist in the data or question
    allowed = set(re.findall(r"\d+", brief + " " + question)) | {str(len(items))}
    if not reply or not set(re.findall(r"\d+", reply)) <= allowed:
        return fallback
    return reply


# ---------- skill-gap answer: plain text from the scoring code ----------
def gap_reply(doc, m):
    n = doc["normalized"]
    title = f"{n.get('job_title') or 'this job'} at {n.get('company') or 'this company'}"
    if not n.get("skills"):
        return f"{title} doesn't list any skills, so I can't work out a skill gap."
    if not m["missing_skills"]:
        return f"Good news: you already have every skill listed for {title}."
    text = f"For {title}, you are missing: {', '.join(m['missing_skills'])}."
    if m["matched_skills"]:
        text += f" You already have: {', '.join(m['matched_skills'])}."
    return text


def _out(intent, reply, items=None, understood=None):
    return {"intent": intent, "reply": reply, "items": items or [], "understood": understood}


# ---------- THE CHATBOT ----------
def answer(message: str, job_id=None, last_job_ids=None) -> dict:
    last_job_ids = last_job_ids or []
    intent = detect_intent(message)

    if intent == "smalltalk":
        return _out(intent, "Hi! Ask me about jobs, for example: "
                            "\"Find Python jobs in Chennai\" or \"Which jobs match my profile?\"")

    if intent in ("matches", "gap"):
        profile = load_profile()
        if not profile_ready(profile):
            return _out(intent, "I need your profile first. Open the Profile tab, add your "
                                "skills (or upload a resume), and save.")

    if intent == "matches":
        items = recommend(profile, 5)
        if not items:
            return _out(intent, "I couldn't find any jobs to match yet.")
        return _out(intent, summarize(message, items), items)

    if intent == "gap":
        jid = resolve_job_id(message, job_id, last_job_ids)
        if not jid:
            return _out(intent, "Which job do you mean? Search for jobs first, then press "
                                "\"Skill gaps?\" under a job, or say \"the first one\".")
        try:
            doc = jobs.find_one({"_id": ObjectId(jid)})
        except InvalidId:
            doc = None
        if not doc or not doc.get("normalized"):
            return _out(intent, "I couldn't find that job.")
        sim = semantic_scores(profile_to_text(profile)).get(jid)
        m = match_job(profile, doc, sim)
        return _out(intent, gap_reply(doc, m), [{**to_public(doc), "match": m}])

    # intent == "search"
    f = understand_query(message)
    flt = build_filter(location=f["location"], skills=f["skills"], fresher=f["fresher"],
                       min_salary_lpa=f["min_salary_lpa"], work_mode=f["work_mode"])
    items = vector_search(f["semantic_text"], flt, 8)
    if not items:
        return _out(intent, "I couldn't find jobs matching that in the database. "
                            "Try fewer conditions, or a different city or skill.", understood=f)
    return _out(intent, summarize(message, items), items, f)
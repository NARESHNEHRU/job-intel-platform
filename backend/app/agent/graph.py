from datetime import datetime, timezone
from typing import Any, Optional, TypedDict

from langgraph.graph import StateGraph, START, END

from backend.app.agent.extract import extract_job
from backend.app.db.mongo import db
from backend.app.db.vector_store import get_collection
from backend.app.services.dedupe import find_duplicate, make_keys
from backend.app.services.embeddings import embed, job_to_text
from backend.app.services.normalize import normalize_job
from backend.app.services.text_utils import build_text
from backend.app.services.validate import validate

jobs = db["jobs"]


# ---------- the STATE: what travels through the graph ----------
class JobState(TypedDict, total=False):
    raw: dict                  # the raw message from MongoDB
    text: str                  # cleaned text
    extracted: dict            # what the AI returned
    cleaned: dict              # after validation
    report: dict               # validation errors/warnings
    normalized: Optional[dict]
    keys: dict                 # duplicate-detection keys
    duplicate_of: Any
    status: str                # ready / duplicate / rejected
    job_id: Any


# ---------- NODES: one function per step ----------
def extract_node(state: JobState):
    text = build_text(state["raw"])
    if len(text) < 20:
        return {"text": text, "extracted": {"is_job": False}}
    return {"text": text, "extracted": extract_job(text)}      # AI step


def validate_node(state: JobState):
    cleaned, report = validate(state["extracted"], state["text"])
    return {
        "cleaned": cleaned,
        "report": report,
        "status": "rejected" if report["errors"] else "pending",
    }


def normalize_node(state: JobState):
    return {"normalized": normalize_job(state["cleaned"])}


def dedupe_node(state: JobState):
    keys = make_keys(state["normalized"], state["text"])
    dup = find_duplicate(jobs, None, keys)
    return {
        "keys": keys,
        "duplicate_of": dup["_id"] if dup else None,
        "status": "duplicate" if dup else "ready",
    }


def save_node(state: JobState):
    raw = state["raw"]
    result = jobs.insert_one({
        "raw_message_id": raw["_id"],                 # link to the original
        "source_chat": raw.get("chat_title"),
        "posted_at": raw.get("posted_at"),
        "input_text": state["text"],
        "extracted": state["extracted"],              # exactly what the AI said
        "validation": state["report"],
        "normalized": state.get("normalized"),
        **state.get("keys", {}),
        "duplicate_of": state.get("duplicate_of"),
        "status": state["status"],
        "embedded": False,
        "created_at": datetime.now(timezone.utc),
    })
    return {"job_id": result.inserted_id}


def embed_node(state: JobState):
    n = state["normalized"]
    text = job_to_text(n)
    get_collection().upsert(
        ids=[str(state["job_id"])],
        embeddings=[embed(text)],
        documents=[text],
        metadatas=[{"company": n.get("company") or "", "title": n.get("job_title") or ""}],
    )
    jobs.update_one({"_id": state["job_id"]}, {"$set": {"embedded": True}})
    return {}


# ---------- DECISIONS (conditional edges) ----------
def after_extract(state: JobState):
    flag = state["extracted"].get("is_job")
    return "validate" if flag is True or str(flag).lower() == "true" else "stop"


def after_validate(state: JobState):
    return "save" if state["status"] == "rejected" else "normalize"


def after_save(state: JobState):
    return "embed" if state["status"] == "ready" else "stop"


# ---------- BUILD THE GRAPH ----------
graph = StateGraph(JobState)
graph.add_node("extract", extract_node)
graph.add_node("validate", validate_node)
graph.add_node("normalize", normalize_node)
graph.add_node("dedupe", dedupe_node)
graph.add_node("save", save_node)
graph.add_node("embed", embed_node)

graph.add_edge(START, "extract")
graph.add_conditional_edges("extract", after_extract, {"validate": "validate", "stop": END})
graph.add_conditional_edges("validate", after_validate, {"save": "save", "normalize": "normalize"})
graph.add_edge("normalize", "dedupe")
graph.add_edge("dedupe", "save")
graph.add_conditional_edges("save", after_save, {"embed": "embed", "stop": END})
graph.add_edge("embed", END)

pipeline = graph.compile()
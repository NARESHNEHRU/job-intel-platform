import ollama

from backend.app.agent.graph import pipeline
from backend.app.db.mongo import db

raw = db["raw_messages"]
MAX_ATTEMPTS = 3


def llm_available() -> bool:
    try:
        ollama.list()
        return True
    except Exception:
        return False


def process_pending(limit: int = 20, verbose: bool = True) -> dict:
    query = {"processed": False,
             "$or": [{"attempts": {"$exists": False}}, {"attempts": {"$lt": MAX_ATTEMPTS}}]}
    todo = list(raw.find(query).sort("posted_at", 1).limit(limit))    # oldest first
    counts = {"attempted": len(todo)}

    for doc in todo:
        try:
            result = pipeline.invoke({"raw": doc})
        except Exception as e:
            raw.update_one({"_id": doc["_id"]}, {"$inc": {"attempts": 1}})
            counts["failed"] = counts.get("failed", 0) + 1
            if verbose:
                print(f"failed    | msg {doc['message_id']} | {e}")
            continue

        status = result.get("status", "not_job")
        counts[status] = counts.get(status, 0) + 1
        if verbose:
            n = result.get("normalized") or {}
            print(f"{status:9} | msg {doc['message_id']} | {n.get('job_title')} @ {n.get('company')}")
        raw.update_one({"_id": doc["_id"]}, {"$set": {"processed": True}})
    return counts
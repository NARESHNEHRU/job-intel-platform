import sys
from backend.app.agent.graph import pipeline
from backend.app.db.mongo import db

raw = db["raw_messages"]
limit = int(sys.argv[1]) if len(sys.argv) > 1 else 20
todo = list(raw.find({"processed": False}).limit(limit))
print(f"Processing {len(todo)} messages...\n")

counts = {}
for doc in todo:
    try:
        result = pipeline.invoke({"raw": doc})
    except Exception as e:
        print(f"failed    | msg {doc['message_id']} | {e}")
        continue                      # stays unprocessed, so it retries next time

    status = result.get("status", "not_job")
    counts[status] = counts.get(status, 0) + 1
    n = result.get("normalized") or {}
    print(f"{status:9} | msg {doc['message_id']} | {n.get('job_title')} @ {n.get('company')}")
    raw.update_one({"_id": doc["_id"]}, {"$set": {"processed": True}})

print("\nSummary:", counts)
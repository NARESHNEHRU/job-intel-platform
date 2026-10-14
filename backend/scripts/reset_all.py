from backend.app.db.mongo import db
from backend.app.db.vector_store import get_client

db["jobs"].drop()
db["raw_messages"].update_many({}, {"$set": {"processed": False, "attempts": 0}})
try:
    get_client().delete_collection("jobs")
except Exception:
    pass
print("Jobs and vectors cleared. Raw messages kept and marked unprocessed.")
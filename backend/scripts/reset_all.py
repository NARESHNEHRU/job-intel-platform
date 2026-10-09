import chromadb
from backend.app.db.mongo import db

db["jobs"].drop()
db["raw_messages"].update_many({}, {"$set": {"processed": False}})
try:
    chromadb.PersistentClient(path="data/chroma").delete_collection("jobs")
except Exception:
    pass
print("Jobs and vectors cleared. Raw messages kept and marked unprocessed.")
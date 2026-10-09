import os
from dotenv import load_dotenv
from pymongo import MongoClient
from backend.app.services.embeddings import embed, job_to_text
from backend.app.db.vector_store import get_collection

load_dotenv()
jobs = MongoClient(os.getenv("MONGO_URI"))["job_platform"]["jobs"]
collection = get_collection()

todo = list(jobs.find({"status": "ready", "embedded": {"$ne": True}}))
print(f"{len(todo)} jobs to embed")

for job in todo:
    n = job["normalized"]
    text = job_to_text(n)
    collection.upsert(
        ids=[str(job["_id"])],
        embeddings=[embed(text)],
        documents=[text],
        metadatas=[{"company": n.get("company") or "", "title": n.get("job_title") or ""}],
    )
    jobs.update_one({"_id": job["_id"]}, {"$set": {"embedded": True}})
    print("  embedded:", n.get("job_title"), "@", n.get("company"))

print("Vectors stored:", collection.count())
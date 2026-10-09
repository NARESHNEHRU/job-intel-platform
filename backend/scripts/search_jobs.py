import os
import sys
from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient
from backend.app.services.embeddings import embed
from backend.app.db.vector_store import get_collection

load_dotenv()
jobs = MongoClient(os.getenv("MONGO_URI"))["job_platform"]["jobs"]
collection = get_collection()

query = " ".join(sys.argv[1:]) or "python developer in chennai"
count = collection.count()
if count == 0:
    sys.exit("No vectors yet. Run embed_jobs first.")

res = collection.query(query_embeddings=[embed(query, "query")], n_results=min(5, count))
print(f"Query: {query}\n")
for job_id, dist in zip(res["ids"][0], res["distances"][0]):
    n = jobs.find_one({"_id": ObjectId(job_id)})["normalized"]
    print(f"{1 - dist:.2f} | {n['job_title']} @ {n['company']}")
    print(f"       {', '.join(n['locations'])} | {', '.join(n['skills'][:6])}")
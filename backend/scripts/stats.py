from backend.app.db.mongo import db
from backend.app.db.vector_store import get_collection

raw, jobs = db["raw_messages"], db["jobs"]

print("Raw messages        :", raw.count_documents({}))
print("  waiting to process:", raw.count_documents({"processed": False, "attempts": {"$not": {"$gte": 3}}}))
print("  gave up (3 fails) :", raw.count_documents({"processed": False, "attempts": {"$gte": 3}}))
print("Jobs by status:")
for s in ("ready", "duplicate", "rejected"):
    print(f"  {s:10}", jobs.count_documents({"status": s}))
print("Ready but not embedded:", jobs.count_documents({"status": "ready", "embedded": {"$ne": True}}))
print("Vectors in Chroma     :", get_collection().count())
print("Jobs with warnings    :", jobs.count_documents({"validation.warnings.0": {"$exists": True}}))

print("\nMost common UNKNOWN skills (add these to the SKILLS dictionary):")
rows = jobs.aggregate([
    {"$match": {"status": "ready"}},
    {"$unwind": "$normalized.unknown_skills"},
    {"$group": {"_id": "$normalized.unknown_skills", "n": {"$sum": 1}}},
    {"$sort": {"n": -1}}, {"$limit": 15},
])
for r in rows:
    print(f"  {r['n']:3} x {r['_id']}")
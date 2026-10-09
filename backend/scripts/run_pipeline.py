import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient
from backend.app.services.validate import validate
from backend.app.services.normalize import normalize_job
from backend.app.services.dedupe import make_keys, find_duplicate

load_dotenv()
jobs = MongoClient(os.getenv("MONGO_URI"))["job_platform"]["jobs"]

drafts = list(jobs.find({"status": "draft"}).sort("posted_at", 1))  # oldest first
print(f"{len(drafts)} draft jobs to process\n")
counts = {"ready": 0, "duplicate": 0, "rejected": 0}
all_unknown = set()

for job in drafts:
    cleaned, report = validate(job["extracted"], job["input_text"])

    if report["errors"]:
        status, norm, keys, dup = "rejected", None, {}, None
    else:
        norm = normalize_job(cleaned)
        keys = make_keys(norm, job["input_text"])
        dup = find_duplicate(jobs, job["_id"], keys)
        status = "duplicate" if dup else "ready"
        all_unknown.update(norm["unknown_skills"])

    jobs.update_one({"_id": job["_id"]}, {"$set": {
        "validation": report,
        "normalized": norm,
        **keys,
        "duplicate_of": dup["_id"] if dup else None,
        "status": status,
        "processed_at": datetime.now(timezone.utc),
    }})
    counts[status] += 1
    title = (norm or {}).get("job_title") or job["extracted"].get("job_title")
    print(f"{status:9} | {title} | warnings: {len(report['warnings'])}")

print("\nSummary:", counts)
if all_unknown:
    print("Unknown skills (add to SKILLS dictionary?):", sorted(all_unknown))
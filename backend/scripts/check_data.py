from backend.app.db.mongo import db

raw, jobs = db["raw_messages"], db["jobs"]
print("Raw messages        :", raw.count_documents({}))
print("  unprocessed       :", raw.count_documents({"processed": False}))
for s in ("ready", "duplicate", "rejected"):
    print(f"Jobs {s:10}     :", jobs.count_documents({"status": s}))
print("Ready, not embedded :", jobs.count_documents({"status": "ready", "embedded": {"$ne": True}}))
print("Jobs with warnings  :", jobs.count_documents({"validation.warnings.0": {"$exists": True}}))
print("Profile saved       :", db["profiles"].count_documents({}))
print("Saved jobs          :", db["saved_jobs"].count_documents({}))
print("Unprocessed raw (no images?):", raw.count_documents({"image_path": {"$exists": True}}), "old image docs")
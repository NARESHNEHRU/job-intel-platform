import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient

from backend.app.services.text_utils import build_text
from backend.app.agent.extract import extract_job


load_dotenv()

db = MongoClient(os.getenv("MONGO_URI"))["job_platform"]

raw = db["raw_messages"]
jobs = db["jobs"]

BATCH = 50

todo = list(
    raw.find({"processed": False}).limit(BATCH)
)

print(f"Processing {len(todo)} messages...")


for doc in todo:

    text = build_text(doc)

    if len(text) < 20:
        raw.update_one(
            {"_id": doc["_id"]},
            {"$set": {"processed": True}}
        )
        continue

    try:
        data = extract_job(text)

    except Exception as error:
        print(f"  failed: {doc['message_id']} -> {error}")
        continue

    if data.get("is_job"):

        jobs.insert_one({
            "raw_message_id": doc["_id"],
            "source_chat": doc["chat_title"],
            "posted_at": doc["posted_at"],
            "input_text": text,
            "extracted": data,
            "status": "draft",
            "created_at": datetime.now(timezone.utc),
        })

        print(
            f"  JOB: {doc['message_id']} -> "
            f"{data.get('job_title')} @ {data.get('company')}"
        )

    else:
        print(f"  not job: {doc['message_id']}")

    raw.update_one(
        {"_id": doc["_id"]},
        {"$set": {"processed": True}}
    )


print("Done.")
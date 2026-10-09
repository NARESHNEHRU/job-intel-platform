import os
import json

from dotenv import load_dotenv
from pymongo import MongoClient

from backend.app.services.text_utils import build_text
from backend.app.agent.extract import extract_job


load_dotenv()

col = MongoClient(os.getenv("MONGO_URI"))["job_platform"]["raw_messages"]


doc = col.find_one({
    "text": {"$nin": [None, ""]}
})

if not doc:
    print("No text message found in MongoDB.")
    exit()


text = build_text(doc)

print("----- TEXT SENT TO AI -----")
print(text)

print("\n----- AI RESULT -----")

result = extract_job(text)

print(json.dumps(result, indent=2, ensure_ascii=False))
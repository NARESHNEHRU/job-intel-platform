import json

from backend.app.db.mongo import db

for job in db["jobs"].aggregate([{"$match": {"status": "ready"}}, {"$sample": {"size": 5}}]):
    print("=" * 70)
    print("ORIGINAL MESSAGE:\n" + job["input_text"])
    print("-" * 70)
    print("WHAT WE STORED:")
    print(json.dumps({k: v for k, v in job["normalized"].items() if v not in (None, [], "")},
                     indent=2, ensure_ascii=False))
    print("WARNINGS:", job["validation"]["warnings"])
import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from pymongo import MongoClient


load_dotenv()

api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
mongo_uri = os.getenv("MONGO_URI")


GROUP_ID = -5315671291
LIMIT = 300


mongo = MongoClient(mongo_uri)
db = mongo["job_platform"]
collection = db["raw_messages"]


collection.create_index(
    [("source", 1), ("chat_id", 1), ("message_id", 1)],
    unique=True
)


saved = 0
skipped = 0


with TelegramClient("job_intel_session", api_id, api_hash) as client:

    group = client.get_entity(GROUP_ID)

    print(f"\nCollecting messages from: {group.title}\n")

    for message in client.iter_messages(group, limit=LIMIT):

        text = (message.text or "").strip()

        # Skip image-only or empty messages
        if len(text) < 20:
            skipped += 1
            continue

        document = {
            "source": "telegram",
            "chat_id": GROUP_ID,
            "chat_title": group.title,
            "message_id": message.id,
            "text": text,
            "posted_at": message.date,
            "processed": False,
        }

        try:
            collection.insert_one(document)

            saved += 1

            print(
                f"Saved message {message.id} "
                f"| {len(text)} characters"
            )

        except Exception as error:

            # Duplicate message
            if "duplicate key error" in str(error).lower():
                skipped += 1
            else:
                print(f"Error saving message {message.id}: {error}")


print("\n--------------------------------")
print(f"Saved: {saved}")
print(f"Skipped: {skipped}")
print("--------------------------------")
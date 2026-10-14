import os

from dotenv import load_dotenv
from pymongo.errors import DuplicateKeyError
from telethon.sync import TelegramClient

from backend.app.db.mongo import db

load_dotenv()
raw = db["raw_messages"]
raw.create_index([("source", 1), ("chat_id", 1), ("message_id", 1)], unique=True)


def channel_ids() -> list[int]:
    return [int(x) for x in os.getenv("TELEGRAM_CHANNEL_IDS", "").split(",") if x.strip()]


def collect(limit: int = 100) -> dict:
    """Save new text posts. Only fetches posts newer than the newest one already saved."""
    api_id = int(os.getenv("TELEGRAM_API_ID"))
    api_hash = os.getenv("TELEGRAM_API_HASH")
    stats = {"saved": 0, "too_short": 0}

    with TelegramClient("data/telegram_session", api_id, api_hash) as client:
        for cid in channel_ids():
            chat = client.get_entity(cid)
            last = raw.find_one({"source": "telegram", "chat_id": cid}, sort=[("message_id", -1)])
            min_id = last["message_id"] if last else 0
            for msg in client.iter_messages(chat, limit=limit, min_id=min_id):
                text = (msg.text or "").strip()
                if len(text) < 20:
                    stats["too_short"] += 1
                    continue
                try:
                    raw.insert_one({
                        "source": "telegram",
                        "chat_id": cid,
                        "chat_title": getattr(chat, "title", None),
                        "message_id": msg.id,
                        "text": text,
                        "posted_at": msg.date,
                        "processed": False,
                    })
                    stats["saved"] += 1
                except DuplicateKeyError:
                    pass
    return stats
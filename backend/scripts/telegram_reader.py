import os
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")

GROUP_ID = -5315671291

client = TelegramClient("job_intel_session", api_id, api_hash)


async def main():
    group = await client.get_entity(GROUP_ID)

    print(f"\nGroup: {group.title}")
    print("Recent messages:\n")

    messages = await client.get_messages(group, limit=5)

    for message in reversed(messages):
        print(f"Message ID: {message.id}")
        print(f"Text: {message.text}")
        print("-" * 60)


with client:
    client.loop.run_until_complete(main())
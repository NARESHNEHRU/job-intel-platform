import os
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")

client = TelegramClient("job_intel_session", api_id, api_hash)


async def main():
    print("\nYour Telegram groups:\n")

    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            print(f"ID: {dialog.id} | Name: {dialog.name}")


with client:
    client.loop.run_until_complete(main())
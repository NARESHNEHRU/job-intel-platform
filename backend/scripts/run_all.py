import sys
import time
from datetime import datetime

from backend.app.agent.runner import llm_available, process_pending
from backend.app.collectors.Telegram import channel_ids, collect

INTERVAL_MIN = 30
BATCH = 20
MAX_BATCHES = 10          # at most 200 messages per cycle


def run_cycle():
    print(f"\n=== {datetime.now():%Y-%m-%d %H:%M} ===")
    if not channel_ids():
        print("No channels set. Add TELEGRAM_CHANNEL_IDS to .env")
        return
    print("Collected:", collect(limit=100))
    if not llm_available():
        print("Ollama is not reachable. Start Ollama. Will retry next cycle.")
        return
    for _ in range(MAX_BATCHES):
        stats = process_pending(BATCH)
        if stats["attempted"] < BATCH:
            break
    print("Cycle finished.")


if __name__ == "__main__":
    once = "--once" in sys.argv
    while True:
        try:
            run_cycle()
        except Exception as e:                  # a network hiccup must not kill the loop
            print("Cycle failed:", e)
        if once:
            break
        print(f"Sleeping {INTERVAL_MIN} minutes (Ctrl+C to stop)")
        time.sleep(INTERVAL_MIN * 60)
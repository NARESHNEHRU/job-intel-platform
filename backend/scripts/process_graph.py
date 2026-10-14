import sys

from backend.app.agent.runner import process_pending

limit = int(sys.argv[1]) if len(sys.argv) > 1 else 20
print("Summary:", process_pending(limit))
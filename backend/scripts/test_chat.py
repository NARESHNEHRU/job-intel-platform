from backend.app.agent.chat import answer

questions = [
    "hello",
    "Find Python jobs in Chennai",
    "Show fresher jobs",
    "Find AI jobs above 5 LPA",
    "Find jobs requiring Python and RAG",
    "Which jobs match my profile?",
    "What skills am I missing for this job?",     # no job given -> should ask which one
]
for q in questions:
    r = answer(q)
    print("Q:", q)
    print("   intent:", r["intent"])
    print("   reply :", r["reply"])
    print("   jobs  :", [(j["job_title"], j["company"]) for j in r["items"]][:4])
    print()

shown = answer("Find jobs")["items"]
if shown:
    r = answer("What skills am I missing for the first one?", last_job_ids=[j["id"] for j in shown])
    print("GAP TEST:", r["reply"])

from backend.app.db.mongo import db
from backend.app.services.profile import load_profile

ready = list(db["jobs"].find({"status": "ready"}))
n = len(ready)


def count(condition):
    return sum(1 for job in ready if condition(job["normalized"]))


print("Ready jobs:", n)
print("  with skills:", count(lambda x: x["skills"]))
print("  with locations:", count(lambda x: x["locations"]))
print("  with salary:", count(lambda x: x["salary_max_inr"]))
print("  with education:", count(lambda x: x["education"]))
print("  experience min = 0:", count(lambda x: x["experience_min_years"] == 0))
print(
    "  experience min missing:",
    count(lambda x: x["experience_min_years"] is None),
)

lost = [
    job for job in ready
    if (job["extracted"].get("skills") or [])
    and not job["normalized"]["skills"]
]
print("AI found skills but validation removed all:", len(lost))

profile = load_profile()
print("\nProfile skills:", profile["skills"])
print("Profile locations:", profile["preferred_locations"])
print("Profile role:", profile["preferred_roles"])

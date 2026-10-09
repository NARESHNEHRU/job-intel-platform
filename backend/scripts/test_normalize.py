from backend.app.services.normalize import *

print(normalize_skills(["ReactJS", "React.js", "react", "python3", "Node JS", "REST APIs", "Kubernetes"]))
print(normalize_locations("BLR / Chennai"))
print(normalize_locations("Amtas Square, Phase 8B, Mohali, Punjab"))
print(parse_salary("4-7 LPA"))
print(parse_salary("15k-20k per month"))
print(parse_salary("Not disclosed"))
print(parse_date("17 Oct 2026"))
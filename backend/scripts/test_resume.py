from backend.app.services.resume import extract_skills
from backend.app.services.degrees import find_degrees

text = ("Skills: Python, ReactJS, Node.js, C++, SQL, REST APIs, Git. "
        "I like Java and JavaScript. B.Tech CSE 2025. Please rest well.")
print(extract_skills(text))
print(find_degrees(text))
import json
import os

import ollama
from dotenv import load_dotenv


load_dotenv()

MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")


SYSTEM_PROMPT = """You extract job information from Telegram job messages.

Return ONLY a JSON object with exactly these keys:
is_job, company, job_title, location, experience_min_years,
experience_max_years, salary_text, skills, education,
employment_type, work_mode, walk_in_date, walk_in_time,
venue, application_deadline, application_url, contact.

Rules:
- is_job is true only if the message announces a job, internship or walk-in drive.
- Use ONLY information written in the message.
- If something is not written, use null or [] for skills.
- NEVER guess or invent information.
- Freshers means experience_min_years is 0.
- Keep salary_text exactly as written.
- Do not convert salary values.
"""


def extract_job(text: str) -> dict:
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        format="json",
        options={"temperature": 0},
    )

    return json.loads(response["message"]["content"])
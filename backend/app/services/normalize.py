import re
from datetime import datetime


def _key(s: str) -> str:
    """'React.js' -> 'reactjs', 'C++' -> 'c++'"""
    return re.sub(r"[^a-z0-9+#]", "", s.lower())


# ---------- SKILLS ----------
# canonical name -> other ways people write it
SKILLS = {
    "Python": ["python3"],
    "JavaScript": ["js", "java script"],
    "TypeScript": ["ts"],
    "React": ["reactjs", "react js"],
    "Node.js": ["node", "nodejs", "node js"],
    "Angular": ["angularjs"],
    "Vue.js": ["vue", "vuejs"],
    "Java": ["core java", "java8"],
    "C": [],
    "C++": ["cpp"],
    "C#": ["csharp", "c sharp"],
    ".NET": ["dotnet", "dot net", "net core", ".net core"],
    "ASP.NET": ["asp.net", "asp net", "asp.net core"],
    "SQL": [],
    "MySQL": [],
    "PostgreSQL": ["postgres"],
    "MongoDB": ["mongo", "mongo db"],
    "Django": [],
    "Flask": [],
    "FastAPI": ["fast api"],
    "Spring Boot": ["springboot", "spring"],
    "REST API": [
        "rest",
        "rest apis",
        "restful",
        "restful api",
        "restful apis",
    ],
    "HTML": ["html5"],
    "CSS": ["css3"],
    "Git": ["github", "git hub"],
    "Docker": [],
    "AWS": ["amazon web services"],
    "Machine Learning": ["ml"],
    "Deep Learning": ["dl"],
    "NLP": ["natural language processing"],
    "Generative AI": ["genai", "gen ai", "generative ai"],
    "RAG": ["retrieval augmented generation"],
    "Excel": ["ms excel", "microsoft excel", "advanced excel"],
    "Power BI": ["powerbi"],
    "Tableau": [],
    "Selenium": [],
    "Manual Testing": [],
    "Data Analysis": ["data analytics"],
}


SKILL_MAP = {}

for canon, variants in SKILLS.items():
    for variant in [canon] + variants:
        SKILL_MAP[_key(variant)] = canon


def normalize_skills(skills):
    """Return (normalized_skills, unknown_skills)."""

    result = []
    unknown = []

    for skill in skills or []:

        if not isinstance(skill, str):
            continue

        skill = skill.strip()

        canon = SKILL_MAP.get(_key(skill))

        if canon:

            if canon not in result:
                result.append(canon)

        elif skill and skill not in result:

            # Keep unknown skills, but remember them
            result.append(skill)
            unknown.append(skill)

    return result, unknown


# ---------- LOCATIONS ----------

CITIES = {
    "Bengaluru": [
        "bangalore",
        "bengaluru",
        "blr",
        "bangaluru",
    ],

    "Chennai": [
        "chennai",
        "madras",
    ],

    "Hyderabad": [
        "hyderabad",
        "hyd",
    ],

    "Mumbai": [
        "mumbai",
        "bombay",
    ],

    "Pune": [
        "pune",
    ],

    "Delhi": [
        "delhi",
        "new delhi",
    ],

    "Gurugram": [
        "gurugram",
        "gurgaon",
    ],

    "Noida": [
        "noida",
    ],

    "Kolkata": [
        "kolkata",
        "calcutta",
    ],

    "Coimbatore": [
        "coimbatore",
        "cbe",
    ],

    "Madurai": [
        "madurai",
    ],

    "Kochi": [
        "kochi",
        "cochin",
    ],

    "Thiruvananthapuram": [
        "thiruvananthapuram",
        "trivandrum",
    ],

    "Ahmedabad": [
        "ahmedabad",
    ],

    "Chandigarh": [
        "chandigarh",
    ],

    "Mohali": [
        "mohali",
        "sas nagar",
        "sahibzada ajit singh nagar",
    ],

    "Pan India": [
        "pan india",
        "across india",
    ],
}


def normalize_locations(text):
    """
    Convert recognized locations into canonical city names.

    Unknown/arbitrary text is discarded instead of being treated
    as a location. This prevents URLs, phone numbers, Zoom IDs,
    venue text, etc. from entering the location filter.
    """

    if not text:
        return []

    low = str(text).lower()

    hits = []

    for canon, aliases in CITIES.items():

        positions = []

        for alias in aliases:

            match = re.search(
                rf"\b{re.escape(alias)}\b",
                low,
            )

            if match:
                positions.append(match.start())

        if positions:
            hits.append(
                (
                    min(positions),
                    canon,
                )
            )

    if hits:
        return [
            canon
            for _, canon in sorted(hits)
        ]

    # IMPORTANT:
    # Do not guess unknown locations.
    #
    # Previously this function converted arbitrary text such as:
    # "Zoom Link: https://us06web.zoom.us/j/81427296039"
    # into fake locations.
    #
    # Unknown location -> no location.
    return []


# ---------- SALARY ----------

def parse_salary(text):
    """
    Return:
        (min_inr_per_year, max_inr_per_year)

    None when salary is unclear.
    """

    if not text:
        return None, None

    text = str(text)

    t = text.lower().replace(",", "")

    nums = [
        float(number)
        for number in re.findall(
            r"\d+(?:\.\d+)?",
            t,
        )
    ][:2]

    if not nums:
        return None, None

    if re.search(
        r"lpa|lakhs?|(?<![a-z])lacs?\b|\d\s*l\b",
        t,
    ):
        multiplier = 100_000

    elif re.search(
        r"\d\s*k\b",
        t,
    ):
        multiplier = 1_000

    else:
        multiplier = 1

    if re.search(
        r"month|\bpm\b|/\s*m\b",
        t,
    ):
        multiplier *= 12

    values = [
        int(round(number * multiplier))
        for number in nums
    ]

    lo = min(values)
    hi = max(values)

    if "up to" in t or "upto" in t:
        lo = None
        hi = values[0]

    salary_value = hi or lo

    if salary_value is not None:

        if not 10_000 <= salary_value <= 100_000_000:
            return None, None

    return lo, hi


# ---------- TYPE / MODE ----------

def normalize_employment_type(text):

    if not text:
        return None

    t = str(text).lower()

    if "intern" in t:
        return "Internship"

    if "contract" in t or "freelance" in t:
        return "Contract"

    if "part" in t:
        return "Part-time"

    if "full" in t or "permanent" in t:
        return "Full-time"

    return str(text).strip().title()


def normalize_work_mode(text):

    if not text:
        return None

    t = str(text).lower()

    if "hybrid" in t:
        return "Hybrid"

    if (
        "remote" in t
        or "wfh" in t
        or "work from home" in t
    ):
        return "Remote"

    if (
        "onsite" in t
        or "on-site" in t
        or "office" in t
        or "wfo" in t
    ):
        return "Onsite"

    return None


# ---------- DATES ----------

DATE_FORMATS = [
    "%d %b %Y",
    "%d %B %Y",
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%d.%m.%Y",
    "%Y-%m-%d",
    "%b %d %Y",
    "%B %d %Y",
]


def parse_date(text):
    """
    Convert:
        '17 Oct 2026'
    into:
        '2026-10-17'

    Return None when unreadable.
    """

    if not text:
        return None

    t = str(text).strip().lower()

    t = re.sub(
        r"(\d+)(st|nd|rd|th)\b",
        r"\1",
        t,
    )

    t = t.replace(",", "")
    t = t.replace("sept", "sep")

    for fmt in DATE_FORMATS:

        try:
            return datetime.strptime(
                t,
                fmt,
            ).date().isoformat()

        except ValueError:
            pass

    return None


# ---------- ALL TOGETHER ----------

def normalize_job(e: dict) -> dict:

    skills, unknown = normalize_skills(
        e.get("skills")
    )

    sal_min, sal_max = parse_salary(
        e.get("salary_text")
    )

    # IMPORTANT:
    # Location must come ONLY from the AI's location field.
    #
    # Do NOT use venue here.
    #
    # Otherwise a Zoom URL or venue text can become a
    # fake location in the location filter.

    locations = normalize_locations(
        e.get("location")
    )

    return {
        "company": (
            e.get("company") or ""
        ).strip() or None,

        "job_title": (
            e.get("job_title") or ""
        ).strip() or None,

        "locations": locations,

        "experience_min_years":
            e.get("experience_min_years"),

        "experience_max_years":
            e.get("experience_max_years"),

        "salary_text":
            e.get("salary_text"),

        "salary_min_inr":
            sal_min,

        "salary_max_inr":
            sal_max,

        "skills":
            skills,

        "unknown_skills":
            unknown,

        "education":
            e.get("education"),

        "employment_type":
            normalize_employment_type(
                e.get("employment_type")
            ),

        "work_mode":
            normalize_work_mode(
                e.get("work_mode")
            ),

        "walk_in_date":
            parse_date(
                e.get("walk_in_date")
            ),

        "walk_in_time":
            e.get("walk_in_time"),

        "venue":
            e.get("venue"),

        "application_deadline":
            parse_date(
                e.get("application_deadline")
            ),

        "application_url":
            e.get("application_url"),

        "contact":
            e.get("contact"),
    }
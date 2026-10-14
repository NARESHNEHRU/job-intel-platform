from backend.app.services.dedupe import make_keys
from backend.app.services.degrees import accepts_any, find_degrees
from backend.app.services.resume import extract_skills

JOB = {"company": "Acme", "job_title": "Python Dev", "locations": ["Chennai"],
       "walk_in_date": None, "application_url": None}


def test_same_text_different_formatting_has_same_hash():
    assert make_keys(JOB, "Hello, World!")["text_hash"] == make_keys(JOB, "hello   world")["text_hash"]


def test_same_job_same_fingerprint():
    other = {**JOB, "company": "ACME"}
    assert make_keys(JOB, "a")["fingerprint"] == make_keys(other, "b")["fingerprint"]


def test_different_city_different_fingerprint():
    other = {**JOB, "locations": ["Pune"]}
    assert make_keys(JOB, "a")["fingerprint"] != make_keys(other, "a")["fingerprint"]


def test_no_url_means_no_url_fingerprint():
    assert make_keys(JOB, "a")["url_fingerprint"] is None


def test_resume_skills():
    text = ("Skills: Python, ReactJS, Node.js, C++, SQL, REST APIs, Git. "
            "I like Java and JavaScript. B.Tech CSE 2025. Please rest well.")
    assert set(extract_skills(text)) == {
        "Python", "React", "Node.js", "C++", "SQL", "REST API", "Git", "Java", "JavaScript"}


def test_word_rest_is_not_a_skill():
    assert extract_skills("please rest well") == []


def test_degrees():
    assert find_degrees("B.Tech CSE 2025") == {"B.E/B.Tech"}
    assert find_degrees("B.E / B.Tech / MCA") == {"B.E/B.Tech", "MCA"}
    assert accepts_any("Any degree") is True
    assert accepts_any("B.Tech") is False
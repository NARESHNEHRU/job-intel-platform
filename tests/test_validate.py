from backend.app.services.validate import validate

TEXT = ("Acme Tech is hiring Python Developers. Skills: Python, SQL. "
        "Apply: https://acme.com/jobs Call 9876543210")


def test_invented_values_are_removed():
    extracted = {
        "company": "Acme Tech", "job_title": "Python Developer",
        "application_url": "https://acme.com/jobs", "salary_text": "10 LPA",   # not in text
        "skills": ["Python", "SQL", "Kubernetes"],                              # Kubernetes not in text
        "contact": "9876543210",
        "experience_min_years": 0, "experience_max_years": 2,
    }
    data, report = validate(extracted, TEXT)
    assert report["errors"] == []
    assert data["salary_text"] is None
    assert data["skills"] == ["Python", "SQL"]
    assert data["application_url"] == "https://acme.com/jobs"
    assert data["contact"] == "9876543210"
    assert len(report["warnings"]) >= 2


def test_fake_url_removed():
    data, _ = validate({"company": "Acme", "job_title": "Dev", "application_url": "https://fake.com"},
                       "Acme is hiring a Dev")
    assert data["application_url"] is None


def test_missing_title_and_company_is_an_error():
    _, report = validate({"company": None, "job_title": None}, "hello")
    assert report["errors"]


def test_swapped_experience_is_fixed():
    data, _ = validate({"company": "Acme", "job_title": "Dev",
                        "experience_min_years": 5, "experience_max_years": 2}, "Acme Dev")
    assert data["experience_min_years"] == 2
    assert data["experience_max_years"] == 5
import re


def _squash(s) -> str:
    """lowercase and keep only letters/digits, so formatting differences don't matter"""
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def _in_text(value, text) -> bool:
    return _squash(value) in _squash(text)


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def validate(extracted: dict, source_text: str):
    """Returns (cleaned_data, report). Never invents anything, only removes."""
    data = dict(extracted)
    errors, warnings = [], []

    # 1. required fields
    if not data.get("job_title") and not data.get("company"):
        errors.append("missing both job_title and company")

    # 2. company/title: keep, but warn if not found in the text
    for field in ("company", "job_title"):
        if data.get(field) and not _in_text(data[field], source_text):
            warnings.append(f"{field} not found in original text")

    # 3. these must appear in the text, otherwise the AI invented them -> remove
    for field in ("application_url", "salary_text", "venue"):
        if data.get(field) and not _in_text(data[field], source_text):
            warnings.append(f"{field} removed (not in original text)")
            data[field] = None

    # 4. contact: every phone/email must appear in the text
    contact = data.get("contact")
    if isinstance(contact, (list, dict)):
        contact = str(contact)
    data["contact"] = contact
    if contact:
        bits = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+|\d{8,}", contact)
        if not bits or not all(_in_text(b, source_text) for b in bits):
            warnings.append("contact removed (not in original text)")
            data["contact"] = None

    # 5. URL shape
    url = data.get("application_url")
    if url and not str(url).startswith(("http://", "https://")):
        warnings.append("application_url is not a valid link, removed")
        data["application_url"] = None

    # 6. experience numbers
    lo, hi = _num(data.get("experience_min_years")), _num(data.get("experience_max_years"))
    if lo is not None and hi is not None and lo > hi:
        warnings.append("experience min > max, swapped")
        lo, hi = hi, lo
    if (lo is not None and not 0 <= lo <= 40) or (hi is not None and not 0 <= hi <= 40):
        warnings.append("experience out of range, removed")
        lo = hi = None
    data["experience_min_years"], data["experience_max_years"] = lo, hi

    # 7. skills: keep only skills that really appear in the text
    skills = data.get("skills") or []
    if not isinstance(skills, list):
        skills = [skills]
    kept = [s for s in skills if isinstance(s, str) and _in_text(s, source_text)]
    if len(kept) < len(skills):
        warnings.append(f"{len(skills) - len(kept)} skill(s) removed (not in text)")
    data["skills"] = kept

    return data, {"errors": errors, "warnings": warnings}
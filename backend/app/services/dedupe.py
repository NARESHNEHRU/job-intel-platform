import hashlib
import re


def _slug(s) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def _hash(s: str) -> str:
    return hashlib.sha1(s.encode()).hexdigest()


def make_keys(n: dict, text: str) -> dict:
    loc = n["locations"][0] if n["locations"] else ""
    keys = {"text_hash": _hash(_slug(text)), "fingerprint": None, "url_fingerprint": None}
    if n.get("company") and n.get("job_title"):
        keys["fingerprint"] = _hash("|".join([
            _slug(n["company"]), _slug(n["job_title"]), _slug(loc),
            n.get("walk_in_date") or ""]))
    if n.get("application_url") and n.get("job_title"):
        url = n["application_url"].lower().rstrip("/")
        keys["url_fingerprint"] = _hash(url + "|" + _slug(n["job_title"]))
    return keys


def find_duplicate(jobs, job_id, keys: dict):
    """Look for an older job that is already accepted."""
    checks = [{"text_hash": keys["text_hash"]}]
    if keys["fingerprint"]:
        checks.append({"fingerprint": keys["fingerprint"]})
    if keys["url_fingerprint"]:
        checks.append({"url_fingerprint": keys["url_fingerprint"]})
    return jobs.find_one({
        "_id": {"$ne": job_id},
        "status": "ready",
        "$or": checks,
    })
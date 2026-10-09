import ollama

EMBED_MODEL = "nomic-embed-text"


def embed(text: str, kind: str = "document") -> list[float]:
    """nomic-embed-text works best with these prefixes."""
    prefix = "search_document: " if kind == "document" else "search_query: "
    resp = ollama.embed(model=EMBED_MODEL, input=prefix + text)
    return resp["embeddings"][0]


def job_to_text(n: dict) -> str:
    """The text that represents a job in vector search."""
    parts = [f"Job title: {n.get('job_title')}", f"Company: {n.get('company')}"]
    if n.get("locations"):
        parts.append("Location: " + ", ".join(n["locations"]))
    if n.get("skills"):
        parts.append("Skills: " + ", ".join(n["skills"]))
    if n.get("education"):
        parts.append(f"Education: {n['education']}")
    lo, hi = n.get("experience_min_years"), n.get("experience_max_years")
    if lo is not None or hi is not None:
        parts.append(f"Experience: {lo if lo is not None else 0} to {hi if hi is not None else 'any'} years")
    if n.get("employment_type"):
        parts.append(f"Type: {n['employment_type']}")
    if n.get("work_mode"):
        parts.append(f"Work mode: {n['work_mode']}")
    return "\n".join(parts)
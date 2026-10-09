import re


DEGREES = {
    "B.E/B.Tech": r"(?i:\bB\.?\s?Tech\b)|\bB\.\s?E\b|\bBE\b",
    "M.E/M.Tech": r"(?i:\bM\.?\s?Tech\b)|\bM\.\s?E\b",
    "MCA": r"(?i:\bMCA\b)",
    "BCA": r"(?i:\bBCA\b)",
    "B.Sc": r"(?i:\bB\.?\s?Sc\b)",
    "M.Sc": r"(?i:\bM\.?\s?Sc\b)",
    "MBA": r"(?i:\bMBA\b)",
}


def find_degrees(text) -> set:
    if isinstance(text, list):
        text = " ".join(str(item) for item in text)

    return {
        name
        for name, pattern in DEGREES.items()
        if re.search(pattern, text or "")
    }


def accepts_any(text) -> bool:
    if isinstance(text, list):
        text = " ".join(str(item) for item in text)

    return bool(
        re.search(
            r"(?i)\bany\s+(degree|graduate|discipline)",
            text or "",
        )
    )
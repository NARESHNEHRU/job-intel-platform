def clean_text(text: str) -> str:
    """Clean unnecessary advertising lines from job messages."""

    keep = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        low = line.lower()

        if "join telegram" in low or "join our" in low:
            continue

        if all(word.startswith("@") for word in line.split()):
            continue

        keep.append(line)

    return "\n".join(keep)


def build_text(doc: dict) -> str:
    """Get and clean the Telegram message text."""

    return clean_text(doc.get("text") or "")
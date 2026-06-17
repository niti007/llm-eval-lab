import re

def normalize_text(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text

def is_complex_query(text: str) -> bool:
    text_l = text.lower()

    complexity_keywords = [
        "compare",
        "analyze",
        "reason",
        "step by step",
        "why",
        "trade-off",
        "architecture",
        "design",
        "evaluate",
        "multi-step",
    ]

    if len(text.split()) > 20:
        return True

    return any(keyword in text_l for keyword in complexity_keywords)
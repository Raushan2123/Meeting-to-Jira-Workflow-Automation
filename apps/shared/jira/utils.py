import re
from typing import Any, Optional, Dict

# Strings that should be treated as empty
NULL_STRINGS = {"", "null", "none", "undefined"}


def clean_str(v: Any) -> Optional[str]:
    """Return a clean string or None."""
    if v is None:
        return None
    s = str(v).strip()
    if s.lower() in NULL_STRINGS:
        return None
    return s


def is_iso_date(s: Optional[str]) -> bool:
    """Validate YYYY-MM-DD"""
    if not s:
        return False
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", s))


def normalize_priority(p: Any) -> Optional[str]:
    """
    Map arbitrary input → Jira-safe priority.
    Only return known valid values.
    """
    p = clean_str(p)
    if not p:
        return None

    mapping = {
        "high": "High",
        "medium": "Medium",
        "low": "Low",
        "highest": "Highest",
        "lowest": "Lowest",
    }
    return mapping.get(p.lower())


def make_safe_title(
    raw_title: Any,
    meeting_summary: str,
    due_date: Optional[str],
    index: int,
) -> str:
    """
    Guarantee a non-empty Jira-safe summary.
    """
    title = clean_str(raw_title) or ""
    title = " ".join(title.split())

    if not title:
        base = meeting_summary.strip() or "Action item"
        if due_date and is_iso_date(due_date):
            title = f"{base} (due {due_date})"
        else:
            title = f"{base} #{index}"

    return title[:255]


def adf_text(text: str) -> Dict:
    """Atlassian Document Format for Jira Cloud."""
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": text or ""}],
            }
        ],
    }

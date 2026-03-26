# calculate_score_certificate.py
# Certificate scoring and display helpers. Reusable for terminal and future UI.
# Uses only Python standard library.

from __future__ import annotations

# Tech elective slot IDs used in both CS and CE plans.
TECH_ELECTIVE_IDS = frozenset({"tech1", "tech2", "tech3", "tech4", "tech5"})


def normalize_keyword(text: str) -> str:
    """Normalize keyword for matching: lowercase, strip, collapse spaces."""
    return " ".join(str(text).strip().lower().split())


def get_unique_certificate_keywords(certificates: dict) -> list[str]:
    """Collect unique keywords across all certificates. Order is stable (sorted)."""
    seen: set[str] = set()
    for cert_data in certificates.values():
        for kw in cert_data.get("keywords") or []:
            n = normalize_keyword(kw)
            if n:
                seen.add(n)
    return sorted(seen)


def score_certificates(certificates: dict, selected_keywords: list[str]) -> dict[str, int]:
    """
    Score each certificate by +1 for each selected keyword it contains.
    Returns dict mapping certificate id -> score.
    """
    scores: dict[str, int] = {}
    selected_set = {normalize_keyword(k) for k in (selected_keywords or []) if normalize_keyword(k)}

    for cert_id, cert_data in certificates.items():
        s = 0
        cert_keywords = cert_data.get("keywords") or []
        cert_norm = {normalize_keyword(k) for k in cert_keywords}
        for sel in selected_set:
            if sel in cert_norm:
                s += 1
        scores[cert_id] = s

    return scores


def get_top_certificates(certificate_scores: dict) -> list[str]:
    """
    Return certificate ids with the highest score. Allows ties.
    If all scores are zero, returns empty list.
    """
    if not certificate_scores:
        return []
    max_score = max(certificate_scores.values())
    if max_score == 0:
        return []
    return [cid for cid, s in certificate_scores.items() if s == max_score]


def tech_electives_relevant(plans: dict) -> bool:
    """
    True if any recommended plan contains at least one tech elective slot
    (tech1, tech2, tech3, tech4, tech5).
    plans: dict mapping option name -> (plan_list, total_credits)
    """
    if not plans:
        return False
    for plan_list, _ in plans.values():
        if any(course in TECH_ELECTIVE_IDS for course in (plan_list or [])):
            return True
    return False


def format_certificate_details(
    cert_name: str, cert_data: dict, score: int | None = None
) -> str:
    """
    Format one certificate for display: name, description, courses, optional score.
    cert_name: display name (e.g. from cert_data["name"] or id).
    cert_data: dict with name, description, courses, etc.
    """
    lines = []
    name = cert_data.get("name") or cert_name
    lines.append(f"  {name}")
    desc = cert_data.get("description") or ""
    if desc:
        lines.append(f"    {desc}")
    courses = cert_data.get("courses") or []
    if courses:
        lines.append(f"    Courses: {', '.join(c.upper() for c in courses)}")
    if score is not None:
        lines.append(f"    Match score: {score}")
    return "\n".join(lines)


def format_certificate_suggestions(
    certificates: dict,
    top_cert_ids: list[str],
    certificate_scores: dict,
    include_score: bool = True,
) -> str:
    """
    Format a block of text for displaying top certificate suggestions.
    If include_score is True, show the score next to each.
    """
    if not top_cert_ids:
        return ""
    lines = [
        "Based on your selected interests, the following certificate(s) may suit you (optional):",
        "",
    ]
    for cid in top_cert_ids:
        cert_data = certificates.get(cid, {})
        score = certificate_scores.get(cid) if include_score else None
        lines.append(format_certificate_details(cid, cert_data, score))
        lines.append("")
    return "\n".join(lines).strip()


def format_all_certificates_with_scores(
    certificates: dict, certificate_scores: dict
) -> str:
    """Format all certificates with their scores for the 'show more options' view."""
    if not certificates:
        return "No certificates defined."
    lines = []
    for cid, cert_data in sorted(certificates.items()):
        score = certificate_scores.get(cid, 0)
        lines.append(format_certificate_details(cid, cert_data, score))
        lines.append("")
    return "\n".join(lines).strip()

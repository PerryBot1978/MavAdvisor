from __future__ import annotations


def normalize_keyword(text: str) -> str:
    """Normalize keyword for matching."""
    return " ".join(str(text).strip().lower().split())


def get_unique_keywords(items: dict) -> list[str]:
    """Collect unique keywords across all items."""
    seen: set[str] = set()

    for item_data in items.values():
        for kw in item_data.get("keywords", []):
            normalized = normalize_keyword(kw)
            if normalized:
                seen.add(normalized)

    return sorted(seen)


def score_items(items: dict, selected_keywords: list[str]) -> dict[str, int]:
    """
    Generic scorer for certificates, clubs, or anything else with keywords.
    Returns: {item_id: score}
    """
    selected_set = {
        normalize_keyword(keyword)
        for keyword in (selected_keywords or [])
        if normalize_keyword(keyword)
    }

    scores: dict[str, int] = {}

    for item_id, item_data in items.items():
        item_keywords = {
            normalize_keyword(keyword)
            for keyword in item_data.get("keywords", [])
            if normalize_keyword(keyword)
        }

        score = 0
        for selected in selected_set:
            if selected in item_keywords:
                score += 1

        scores[item_id] = score

    return scores


def get_top_items(item_scores: dict[str, int]) -> list[str]:
    """Return all item ids tied for top score, excluding all-zero results."""
    if not item_scores:
        return []

    max_score = max(item_scores.values())
    if max_score == 0:
        return []

    return [item_id for item_id, score in item_scores.items() if score == max_score]


def rank_items(items: dict, selected_keywords: list[str]) -> list[dict]:
    """
    Return sorted item records with score included.
    Highest score first, then alphabetical by name.
    """
    scores = score_items(items, selected_keywords)

    ranked = []
    for item_id, item_data in items.items():
        ranked.append({
            "id": item_id,
            "name": item_data.get("name", item_id),
            "description": item_data.get("description", ""),
            "score": scores[item_id],
            "keywords": item_data.get("keywords", []),
        })

    ranked.sort(key=lambda item: (-item["score"], item["name"].lower()))
    return ranked


def build_suggestions(items: dict, selected_keywords: list[str], item_label: str = "item") -> list[dict]:
    """
    Build API-friendly suggestion objects.
    Example output:
    [
        {"item_id": "cyber_security", "item_name": "Cyber Security", "score": 2}
    ]
    """
    scores = score_items(items, selected_keywords)

    suggestions = []
    for item_id, score in scores.items():
        suggestions.append({
            f"{item_label}_id": item_id,
            f"{item_label}_name": items[item_id].get("name", item_id),
            "score": score,
        })

    suggestions.sort(key=lambda x: (-x["score"], x[f"{item_label}_name"].lower()))
    return suggestions
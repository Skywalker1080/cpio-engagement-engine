"""
Utility module for keyword indexing and matching across different platforms.
"""

def build_keyword_index(keywords_data: dict) -> dict[str, str]:
    """
    Flatten the categorized keyword dict into a lookup:
      { "mvrv": "on_chain_analytics", "glassnode": "competitor_mentions", ... }

    All keys are lowercased for case-insensitive matching.
    """
    index: dict[str, str] = {}
    for category, words in keywords_data.items():
        for word in words:
            index[word.lower()] = category
    return index


def find_keyword_matches(text: str, keyword_index: dict[str, str]) -> list[dict]:
    """
    Scan *text* for any keywords present in *keyword_index*.

    Returns a list of dicts: [{"keyword": "MVRV", "category": "on_chain_analytics"}, ...]
    """
    # Defensive check against None text
    if not text:
        return []
        
    text_lower = text.lower()
    matches: list[dict] = []
    seen: set[str] = set()

    for keyword, category in keyword_index.items():
        if keyword in text_lower and keyword not in seen:
            matches.append({"keyword": keyword, "category": category})
            seen.add(keyword)

    return matches

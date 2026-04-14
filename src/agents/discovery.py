"""
Discovery Agent (minimal version).

Evaluates an incoming message and produces a lightweight "signal" dict
that downstream agents (responder, publisher) consume.
"""

import logging

logger = logging.getLogger("discovery")


def evaluate_message(
    text: str,
    author_name: str,
    channel_name: str,
    matched_keywords: list[dict],
) -> dict:
    """
    Score and package a message into a signal dict.

    Scoring heuristic (simple, no ML):
      - Base score: 10 per keyword matched
      - +15  if message contains a question mark (high-intent)
      - +10  if message is longer than 100 chars (detailed post)
      - +20  if a competitor is mentioned (high-value conversation)

    Returns:
        {
            "text":       str,
            "author":     str,
            "channel":    str,
            "keywords":   [{"keyword": ..., "category": ...}, ...],
            "categories": set → list,
            "score":      int,
            "is_question": bool,
        }
    """
    score = len(matched_keywords) * 10

    is_question = "?" in text
    if is_question:
        score += 15

    if len(text) > 100:
        score += 10

    categories = list({m["category"] for m in matched_keywords})

    if "competitor_mentions" in categories:
        score += 20

    signal = {
        "text": text,
        "author": author_name,
        "channel": channel_name,
        "keywords": matched_keywords,
        "categories": categories,
        "score": score,
        "is_question": is_question,
    }

    logger.info("Signal scored %d for message by %s in #%s",
                score, author_name, channel_name)
    return signal

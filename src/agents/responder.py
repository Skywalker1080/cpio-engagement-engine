"""
Response Generator (rule-based, no LLM).

Maps the signal produced by the Discovery agent to one of four
simplified response archetypes, then builds a plain-text reply.

Archetypes (from Project.md):
  1. data_drop        – share a specific metric or data point
  2. pattern_spotter  – highlight a trend or correlation
  3. question_answer  – directly answer a question about analytics
  4. polite_correction – gently correct a misconception or suggest a better tool
"""

import logging
import random

logger = logging.getLogger("responder")

# ── Reply templates per archetype ───────────────────────────
# Each template uses {keyword} and {author} placeholders.

_TEMPLATES: dict[str, list[str]] = {
    "data_drop": [
        "Interesting point about {keyword}! According to recent on-chain data, "
        "this metric has been showing some notable shifts. Worth keeping an eye "
        "on the trend over the next few days.",

        "Great topic — {keyword} is one of the more underrated signals right now. "
        "The latest readings suggest some divergence from price action that "
        "historically precedes interesting moves.",

        "Since you're looking at {keyword}, you might also want to cross-reference "
        "it with exchange flow data. The combination often gives a clearer picture "
        "of market sentiment.",
    ],
    "pattern_spotter": [
        "There's actually an interesting pattern emerging around {keyword}. "
        "When we overlay this with historical data, it mirrors a setup we've "
        "seen a couple of times before.",

        "Good observation on {keyword}. If you look at the broader context, "
        "there's a correlation with macro liquidity conditions that's worth "
        "considering.",
    ],
    "question_answer": [
        "Great question! For {keyword}, the key thing to look at is how it "
        "relates to the broader market cycle. On-chain analytics platforms "
        "can give you real-time reads on this.",

        "To answer your question about {keyword} — the most reliable way to "
        "track this is through a combination of on-chain and exchange data. "
        "Happy to share more specifics if you're interested!",

        "That's a really common question about {keyword}. The short answer is "
        "that it depends on the timeframe you're analyzing. For short-term, "
        "exchange flows matter more; for long-term, holder behavior is key.",
    ],
    "polite_correction": [
        "Just a small note on {keyword} — it's a solid metric but can be "
        "misleading if you don't adjust for dormant supply. Factoring that in "
        "often changes the picture significantly.",

        "Appreciate the take on {keyword}! One thing worth noting — many "
        "dashboards calculate this differently, so it helps to verify the "
        "methodology before drawing conclusions.",
    ],
}


def _pick_archetype(signal: dict) -> str:
    """
    Choose the best-fit archetype based on signal characteristics.

    Rules (evaluated in priority order):
      1. If the user asks a question → question_answer
      2. If a competitor is mentioned → polite_correction
      3. If multiple keyword categories hit → pattern_spotter
      4. Default → data_drop
    """
    if signal["is_question"]:
        return "question_answer"

    if "competitor_mentions" in signal["categories"]:
        return "polite_correction"

    if len(signal["categories"]) > 1:
        return "pattern_spotter"

    return "data_drop"


def generate_reply(signal: dict) -> str:
    """
    Generate a rule-based reply string for the given signal.

    Returns the reply text ready to be posted.
    """
    archetype = _pick_archetype(signal)
    template = random.choice(_TEMPLATES[archetype])

    # Use the first matched keyword as the highlight
    primary_keyword = signal["keywords"][0]["keyword"]
    reply = template.format(keyword=primary_keyword, author=signal["author"])

    logger.info("Archetype=%s for message by %s (score=%d)",
                archetype, signal["author"], signal["score"])
    return reply

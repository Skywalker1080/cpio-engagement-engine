"""
Discord Gateway WebSocket bot.

Listens to all messages in the configured guild and checks them
against the keyword list from keywords.json.  When a match is found,
hands the message off to the orchestrator pipeline.
"""

import logging
import discord
from src.config import load_keywords
from src.orchestrator import process_message

logger = logging.getLogger("discord_monitor")


def _build_keyword_index(keywords_data: dict) -> dict[str, str]:
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
    text_lower = text.lower()
    matches: list[dict] = []
    seen: set[str] = set()

    for keyword, category in keyword_index.items():
        if keyword in text_lower and keyword not in seen:
            matches.append({"keyword": keyword, "category": category})
            seen.add(keyword)

    return matches


def setup(client: discord.Client) -> None:
    """
    Register the on_message event handler on the given Discord client.
    Call this once at startup from main.py.
    """
    keywords_data = load_keywords()
    keyword_index = _build_keyword_index(keywords_data)
    logger.info("Loaded %d keywords across %d categories",
                len(keyword_index), len(keywords_data))

    @client.event
    async def on_message(message: discord.Message) -> None:
        # Never respond to ourselves
        if message.author == client.user:
            return

        # Ignore DMs — we only operate in guild channels
        if message.guild is None:
            return

        matches = find_keyword_matches(message.content, keyword_index)
        if not matches:
            return

        logger.info(
            "Keyword hit in #%s by %s — matched: %s",
            message.channel.name,
            message.author.name,
            [m["keyword"] for m in matches],
        )

        # Hand off to the pipeline (orchestrator runs discovery → responder → publisher)
        await process_message(message, matches)
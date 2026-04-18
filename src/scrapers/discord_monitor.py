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


from src.text_matcher import build_keyword_index, find_keyword_matches

def setup(client: discord.Client) -> None:
    """
    Register the on_message event handler on the given Discord client.
    Call this once at startup from main.py.
    """
    keywords_data = load_keywords()
    keyword_index = build_keyword_index(keywords_data)
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
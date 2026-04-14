"""
Entry point for the CryptoPrism Discord Engagement Bot.

Initializes the Discord client with required intents,
registers the discord_monitor event handlers, and starts the bot.
"""

import logging
import discord

from src.config import DISCORD_TOKEN
from src.scrapers import discord_monitor

# ── Logging ───────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-18s │ %(levelname)-5s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("main")


def main() -> None:
    """Boot the Discord bot."""
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN is not set. Check your .env file.")
        raise SystemExit(1)

    # We need message_content intent to read message bodies
    intents = discord.Intents.default()
    intents.message_content = True

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready() -> None:
        logger.info("Bot connected as %s (ID: %s)", client.user.name, client.user.id)
        logger.info("Monitoring %d guild(s)", len(client.guilds))

    # Wire up the keyword scanner
    discord_monitor.setup(client)

    logger.info("Starting Discord bot...")
    client.run(DISCORD_TOKEN, log_handler=None)


if __name__ == "__main__":
    main()

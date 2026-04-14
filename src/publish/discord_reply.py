"""
Discord Bot API message publisher.

Sends the generated reply back to the originating Discord channel
with a randomized delay to mimic human typing speed
(per Project.md anti-spam guardrails).
"""

import asyncio
import logging
import random
import discord

logger = logging.getLogger("discord_reply")

# Human-speed delay range in seconds
_MIN_DELAY = 2
_MAX_DELAY = 8


async def send_reply(channel: discord.TextChannel, reply_text: str) -> bool:
    """
    Send *reply_text* to *channel* after a random human-speed delay.

    Returns True on success, False on failure.
    """
    delay = random.uniform(_MIN_DELAY, _MAX_DELAY)
    logger.info("Waiting %.1fs before replying in #%s", delay, channel.name)
    await asyncio.sleep(delay)

    try:
        await channel.send(reply_text)
        logger.info("Reply sent to #%s", channel.name)
        return True
    except discord.Forbidden:
        logger.error("Missing permissions to send message in #%s", channel.name)
        return False
    except discord.HTTPException as exc:
        logger.error("Failed to send message in #%s: %s", channel.name, exc)
        return False

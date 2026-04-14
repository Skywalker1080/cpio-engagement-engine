"""
Orchestrator — the glue that runs the pipeline.

Flow: message → discovery (score) → responder (generate reply) → publisher (send) → log
"""

import json
import logging
from datetime import datetime, timezone

import discord

from src.agents.discovery import evaluate_message
from src.agents.responder import generate_reply
from src.publish.discord_reply import send_reply
from src.config import INTERACTIONS_LOG

logger = logging.getLogger("orchestrator")


def _log_interaction(signal: dict, reply_text: str, sent: bool) -> None:
    """
    Append an interaction record to the JSON log file.
    Uses a simple append-to-list strategy (fine for MVP, no DB needed).
    """
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "author": signal["author"],
        "channel": signal["channel"],
        "message_text": signal["text"][:500],  # truncate very long messages
        "matched_keywords": signal["keywords"],
        "score": signal["score"],
        "reply": reply_text,
        "sent": sent,
    }

    # Read existing log or start fresh
    try:
        with open(INTERACTIONS_LOG, "r", encoding="utf-8") as f:
            log_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        log_data = []

    log_data.append(record)

    with open(INTERACTIONS_LOG, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)

    logger.info("Interaction logged (%d total records)", len(log_data))


async def process_message(
    message: discord.Message,
    matched_keywords: list[dict],
) -> None:
    """
    Run the full pipeline for a keyword-matched Discord message.

    Steps:
      1. Discovery — evaluate & score the message
      2. Responder — generate a rule-based reply
      3. Publisher — send the reply to the channel
      4. Logger   — persist the interaction to JSON
    """
    # 1. Discovery
    signal = evaluate_message(
        text=message.content,
        author_name=message.author.name,
        channel_name=message.channel.name,
        matched_keywords=matched_keywords,
    )

    # Skip low-quality signals (score below threshold)
    if signal["score"] < 10:
        logger.info("Signal score %d below threshold, skipping", signal["score"])
        return

    # 2. Responder
    reply_text = generate_reply(signal)

    # 3. Publisher
    sent = await send_reply(message.channel, reply_text)

    # 4. Log
    _log_interaction(signal, reply_text, sent)

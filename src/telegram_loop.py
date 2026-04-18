"""
Run a testing loop for Telegram:
Fetches messages via Apify, finds keyword matches, evaluates score,
generates a response, and logs it to local files.
"""

import sys
import asyncio
import logging
import argparse
from typing import Any, Dict

from src.config import APIFY_TOKEN, load_keywords
from src.text_matcher import build_keyword_index, find_keyword_matches
from src.scrapers.telegram_scraper import fetch_telegram_messages
from src.scrapers.telegram_user_scraper import search_telegram_user_history
from src.agents.discovery import evaluate_message
from src.agents.responder import generate_reply
from src.publish.telegram_reply import send_telegram_user_reply
from src.orchestrator import _log_interaction

# Configure basic logging for the script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("telegram_loop")


def extract_message_data(item: Dict[str, Any]) -> tuple[str, str, str, str]:
    """
    Extracts text, author, channel, and message_url from an Apify Telegram item.
    """
    # Telegram items usually have 'message' or 'text'
    text = item.get("message", "") or item.get("text", "")
    
    # Author might be 'sender', 'from', or 'sender_id'
    author = str(item.get("sender_id", "")) or item.get("sender", "") or item.get("from", "unknown_user")
    
    # Channel might be 'channelName', 'channel', or 'chat_title'
    channel_name = item.get("chat_title", "") or item.get("channelName", "") or item.get("channel", "unknown_channel")
    
    # URL might be 'messageUrl' or 'url'
    message_url = item.get("messageUrl", "") or item.get("url", "")
    
    # Message ID for replies
    msg_id = item.get("message_id") or item.get("id") or item.get("messageId")
    try:
        msg_id = int(msg_id)
    except (ValueError, TypeError):
        msg_id = None
        
    # Chat ID (Numeric target ideally, used mostly by User API)
    chat_numeric_id = item.get("chat_id")
    if chat_numeric_id is not None:
        try:
            chat_numeric_id = int(chat_numeric_id)
        except (ValueError, TypeError):
            chat_numeric_id = None
            
    return text, author, channel_name, message_url, msg_id, chat_numeric_id


async def process_telegram_message(item: Dict[str, Any], keyword_index: dict[str, str], live_reply: bool = False) -> None:
    """
    Process a single Telegram message through the matching, scoring, and generating pipeline.
    """
    text, author, channel, message_url, msg_id, chat_numeric_id = extract_message_data(item)
    
    if not text:
        return
        
    matches = find_keyword_matches(text, keyword_index)
    if not matches:
        return
        
    logger.info("Keyword hit in t.me/%s by %s - matched: %s", 
                channel, author, [m["keyword"] for m in matches])
                
    # 1. Discovery
    signal = evaluate_message(
        text=text,
        author_name=author,
        channel_name=channel,
        matched_keywords=matches,
    )
    
    # Skip low-quality signals (score below threshold)
    if signal["score"] < 10:
        logger.info("Signal score %d below threshold, skipping", signal["score"])
        return
        
    # 2. Responder
    reply_text = await generate_reply(signal)
    
    # 3. Publish
    sent = False
    if live_reply:
        # Prefer the exact numeric ID if we have it, otherwise fallback to the channel name
        target_entity = chat_numeric_id if chat_numeric_id else (channel if channel else "me")
        
        # If item came from User API scraper, it has an active Telethon client attached
        t_client = item.get("_client")
        
        sent = await send_telegram_user_reply(target_entity, reply_text, reply_to_msg_id=msg_id, client=t_client)

    # 4. Log
    _log_interaction(signal, reply_text, sent=sent)


async def main():
    parser = argparse.ArgumentParser(description="Telegram Fetch-and-Reply Testing Loop")
    parser.add_argument(
        "--channels", 
        nargs="*", 
        default=["cointelegraph"], 
        help="One or more Telegram channels to fetch messages from."
    )
    parser.add_argument(
        "--max-messages",
        "--limit",
        dest="max_messages",
        type=int,
        default=10,
        help="Maximum messages to fetch per channel/keyword."
    )
    parser.add_argument(
        "--reply",
        action="store_true",
        help="Actually send the reply using your Telegram User account."
    )
    args = parser.parse_args()

    if not APIFY_TOKEN:
        logger.error("Missing APIFY_TOKEN in environment (.env). Ensure it is set before running.")
        sys.exit(1)

    # Setup Keywords
    try:
        keywords_data = load_keywords()
        keyword_index = build_keyword_index(keywords_data)
        logger.info("Loaded %d keywords.", len(keyword_index))
    except Exception as exc:
        logger.error("Failed to load keywords: %s", exc)
        sys.exit(1)

    search_keywords_global = list(keyword_index.keys())

    # 1. Try Native User API Scraper
    user_api_success = False
    logger.info("Attempting to search via Telegram User API...")
    try:
        # User API optionally uses specific channels, otherwise searches globally
        # Because User API is an async generator, we use `async for`
        
        # If user provided a specific channel, search inside it. If None, search across all.
        target_channels = args.channels if args.channels != ["cointelegraph"] else None
        
        async for item in search_telegram_user_history(
            keywords=search_keywords_global, 
            channels=target_channels, 
            limit_per_keyword=args.max_messages
        ):
            user_api_success = True
            await process_telegram_message(item, keyword_index, live_reply=args.reply)
            
    except Exception as e:
        logger.warning(f"User API scraping failed or was interrupted: {e}")

    # 2. Apify Fallback
    if not user_api_success:
        logger.info("User API yielded no results or failed. Falling back to Apify cloud scraper...")
        
        # Determine mode for Apify
        search_keywords_apify = search_keywords_global if not args.channels else None

        for item in fetch_telegram_messages(
            apify_token=APIFY_TOKEN, 
            channels=args.channels, 
            keywords=search_keywords_apify,
            max_messages=args.max_messages
        ):
            await process_telegram_message(item, keyword_index, live_reply=args.reply)

    logger.info("Telegram loop finished.")


if __name__ == "__main__":
    asyncio.run(main())

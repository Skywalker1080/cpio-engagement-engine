"""
Run a testing loop for Reddit:
Fetches posts via Apify, finds keyword matches, evaluates score,
generates a response, and logs it to local files without actually posting.
"""

import sys
import asyncio
import logging
import argparse
from typing import Any, Dict

from src.config import APIFY_TOKEN, load_keywords
from src.text_matcher import build_keyword_index, find_keyword_matches
from src.scrapers.reddit_scraper import fetch_reddit_posts
from src.agents.discovery import evaluate_message
from src.agents.responder import generate_reply
from src.publish.reddit_comment import post_reddit_comment
from src.orchestrator import _log_interaction

# Configure basic logging for the script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("reddit_loop")


def extract_post_data(item: Dict[str, Any]) -> tuple[str, str, str, str]:
    """
    Extracts text, author, channel, and post_id from an Apify Reddit item.
    Titles and body texts are combined.
    """
    title = item.get("title", "")
    body = item.get("selftext", "") or item.get("text", "") or item.get("body", "")
    text = f"{title}\n{body}".strip()
    
    author = item.get("author", "unknown_user")
    
    # Exclude the "r/" prefix if it's there
    channel_name = item.get("subreddit", "unknown_subreddit")
    
    post_url = item.get("url", "")
    
    return text, author, channel_name, post_url


async def process_reddit_post(item: Dict[str, Any], keyword_index: dict[str, str], dry_run: bool = True) -> None:
    """
    Process a single Reddit post through the matching, scoring, and generating pipeline.
    """
    text, author, channel, post_url = extract_post_data(item)
    
    if not text:
        return
        
    matches = find_keyword_matches(text, keyword_index)
    if not matches:
        return
        
    logger.info("Keyword hit in r/%s by %s - matched: %s", 
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
    if not dry_run and post_url:
        post_result = post_reddit_comment(post_url, reply_text, dry_run=False)
        sent = post_result.get("status") == "success"
    else:
        post_reddit_comment(post_url, reply_text, dry_run=True)
        sent = False
    
    # 4. Log
    _log_interaction(signal, reply_text, sent=sent)


async def main():
    parser = argparse.ArgumentParser(description="Reddit Fetch-and-Reply Testing Loop")
    parser.add_argument(
        "--urls", 
        nargs="+", 
        default=[
            "https://www.reddit.com/r/CryptoCurrency/",
            "https://www.reddit.com/r/CryptoMarkets/"
        ], 
        help="One or more Reddit URLs to fetch posts from."
    )
    parser.add_argument(
        "--post",
        action="store_true",
        help="Actually post the comment to Reddit rather than dry run."
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

    # Fetch and process
    for item in fetch_reddit_posts(APIFY_TOKEN, args.urls):
        await process_reddit_post(item, keyword_index, dry_run=not args.post)

    logger.info("Reddit loop finished.")


if __name__ == "__main__":
    asyncio.run(main())

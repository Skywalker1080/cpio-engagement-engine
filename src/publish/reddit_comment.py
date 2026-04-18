"""
Post a reply to a Reddit thread via Apify's reddit-poster actor.
"""
import logging
import json
from pathlib import Path
from apify_client import ApifyClient
from src.config import (
    APIFY_TOKEN,
    REDDIT_USERNAME,
    REDDIT_PASSWORD
)

logger = logging.getLogger("reddit_comment")

# Path to the cookies JSON file
COOKIES_PATH = Path("src/safety/reddit_cookies.json")

def post_reddit_comment(post_url: str, comment_text: str, dry_run: bool = True, post_type: str = "comment", title: str = None, subreddit: str = "") -> dict:
    """
    Replies to a Reddit post or creates a new post using Apify reddit-poster actor.
    Automatically loads cookies from COOKIES_PATH if available.
    """
    if dry_run:
        logger.info(f"[DRY_RUN] Would have replied to {post_url} via Apify with: {comment_text[:50]}...")
        return {"status": "success", "demoMode": True}

    if not APIFY_TOKEN:
        logger.error("Missing APIFY_TOKEN.")
        return {"status": "error", "error": "Missing credentials"}

    # Load cookies if the JSON file exists
    cookies_string = ""
    if COOKIES_PATH.exists():
        try:
            with open(COOKIES_PATH, "r") as f:
                cookies_data = json.load(f)
                cookies_string = json.dumps(cookies_data)
                logger.info("Loaded Reddit cookies from src/safety/reddit_cookies.json")
        except Exception as e:
            logger.warning(f"Failed to load cookies from {COOKIES_PATH}: {e}")

    try:
        client = ApifyClient(APIFY_TOKEN)

        run_input = {
            "username": REDDIT_USERNAME or "",
            "password": REDDIT_PASSWORD or "",
            "cookies": cookies_string,
            "subreddit": subreddit or "",
            "postType": post_type,
            "title": title or "",
            "content": comment_text,
            "linkUrl": "",
            "imageUrl": "",
            "replyToUrl": post_url or "",
            "flair": "",
            "nsfw": False,
            "spoiler": False,
            "timeout": 120,
            "demoMode": False,
            "webhookUrl": "",
            "indexNowKey": "",
            "utmTracking": { "enabled": True },
            "cookieStorageKey": "",
            "cookieKvStoreName": "cookie-sessions",
            "proxy": {
                "useApifyProxy": True,
                "apifyProxyGroups": ["RESIDENTIAL"]
            }
        }

        # Run the Actor and wait for it to finish
        logger.info(f"Calling Apify to post a Reddit comment to {post_url} (with residential proxy)")
        run = client.actor("awk3vCKp45tkwaTaB").call(run_input=run_input)

        items = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            items.append(item)
            
        logger.info(f"Apify commenting to Reddit returned: {items}")
        
        return {
            "status": "success",
            "apify_items": items
        }
    except Exception as exc:
        logger.error(f"Failed to post comment to Reddit via Apify: {exc}")
        return {"status": "error", "error": str(exc)}

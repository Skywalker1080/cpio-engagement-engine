"""
Telegram scraper wrapper using Apify.
"""

import logging
from typing import Generator, Dict, Any
from apify_client import ApifyClient

logger = logging.getLogger("telegram_scraper")

def fetch_telegram_messages(
    apify_token: str, 
    channels: list[str] = None, 
    keywords: list[str] = None,
    max_messages: int = 100
) -> Generator[Dict[str, Any], None, None]:
    """
    Connect to Telegram via Apify Actor to fetch messages from channels or by keywords.
    Yields parsed dict items containing the message details.
    """
    if not apify_token:
        logger.error("Missing Apify Token.")
        return

    client = ApifyClient(apify_token)

    # Prepare the Actor input based on whether channels or keywords are provided
    # Defaulting to channel mode if channels are provided
    mode = "channel" if channels else "search"
    
    # Ensure minimum of 10 for validation (actor requirement)
    clamped_messages = max(10, max_messages)

    run_input = {
        "mode": mode,
        "keywords": keywords or [],
        "afterDate": None,
        "beforeDate": None,
        "maxResultsPerKeyword": clamped_messages if mode == "search" else 100,
        "countryCode": "us",
        "languageCode": "en",
        "channels": channels or [],
        "channelMaxMessages": clamped_messages if mode == "channel" else 100,
        "channelAfterDate": None,
    }

    logger.info(f"Starting Apify run for Telegram in {mode} mode.")
    try:
        # Run the Actor and wait for it to finish
        run = client.actor("kCdMrRb7UiSRSFYeO").call(run_input=run_input)

        if "defaultDatasetId" in run:
            dataset_id = run["defaultDatasetId"]
            logger.info(f"Apify run finished. Fetching results from dataset: {dataset_id}")
            for item in client.dataset(dataset_id).iterate_items():
                yield item
        else:
            logger.warning("No dataset ID found in Apify run outcome.")
    except Exception as exc:
        logger.error(f"Failed to fetch Telegram messages via Apify: {exc}")

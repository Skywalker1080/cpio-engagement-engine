"""
Reddit scraper using Apify.
"""

import logging
from apify_client import ApifyClient
from typing import Generator, Dict, Any

logger = logging.getLogger("reddit_scraper")

def fetch_reddit_posts(apify_token: str, start_urls: list[str]) -> Generator[Dict[str, Any], None, None]:
    """
    Connect to Reddit via Apify Actor to fetch relative posts.
    Yields parsed dict items containing the post details.
    """
    if not apify_token:
        logger.error("Missing Apify Token.")
        return

    # Initialize the ApifyClient
    client = ApifyClient(apify_token)

    # Prepare the Actor input using the provided snippet style
    target_urls = [{"url": url} for url in start_urls]
    
    run_input = {
        "startUrls": target_urls,
        "skipComments": False,
        "skipUserPosts": False,
        "skipCommunity": False,
        "searches": [],
        "searchCommunityName": "",
        "ignoreStartUrls": False,
        "searchPosts": True,
        "searchComments": False,
        "searchCommunities": False,
        "searchUsers": False,
        "sort": "new",
        "time": "all",
        "includeNSFW": True,
        "maxItems": 10,
        "maxPostCount": 10,
        "postDateLimit": "",
        "commentDateLimit": "",
        "maxComments": 10,
        "maxCommunitiesCount": 2,
        "maxUserCount": 2,
        "scrollTimeout": 40,
        "proxy": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"],
        },
        "debugMode": False,
    }

    logger.info("Starting Apify run for Reddit URLs: %s", start_urls)
    try:
        # Run the Actor and wait for it to finish
        run = client.actor("oAuCIx3ItNrs2okjQ").call(run_input=run_input)

        # Fetch and yield Actor results from the run's dataset
        if "defaultDatasetId" in run:
            dataset_id = run["defaultDatasetId"]
            logger.info("Apify run finished. Fetching results from dataset: %s", dataset_id)
            for item in client.dataset(dataset_id).iterate_items():
                yield item
        else:
            logger.warning("No dataset ID found in Apify run outcome.")
    except Exception as exc:
        logger.error("Failed to fetch Reddit posts via Apify: %s", exc)

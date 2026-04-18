import logging
from src.publish.reddit_comment import post_reddit_comment

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("live_sample_post")

def run_sample_post():
    subreddit = "Cryptoprismio"
    title = "CryptoPrism Engine - Live Operational Test"
    content = "The CryptoPrism engagement engine is now fully operational with unified Apify integration and residential proxy tunneling. \n\nTesting discovery + publishing pipelines."
    
    logger.info(f"Posting to r/{subreddit}...")
    
    # We use post_reddit_comment but pass custom parameters for a new text post
    result = post_reddit_comment(
        post_url="", # Empty for new post
        comment_text=content,
        dry_run=False,
        post_type="text",
        title=title,
        subreddit=subreddit
    )
    
    if result.get("status") == "success":
        logger.info(f"Successfully triggered post to r/{subreddit}")
    else:
        logger.error(f"Failed to post: {result.get('error')}")

if __name__ == "__main__":
    run_sample_post()

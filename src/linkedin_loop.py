import os
import sys
import logging
import argparse

from src.publish.linkedin_client import LinkedInClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("LinkedInLoop")

def main():
    parser = argparse.ArgumentParser(description="LinkedIn Engagement Loop (Auth and Post only for now)")
    parser.add_argument("--auth", action="store_true", help="Authenticate with LinkedIn to get an Access Token")
    parser.add_argument("--post", type=str, help="Make a sample post to verify functionality", metavar="TEXT")

    args = parser.parse_args()

    client = LinkedInClient()

    if args.auth:
        logger.info("Starting LinkedIn Authentication flow...")
        success = client.authenticate()
        if success:
            logger.info("Authentication complete. Token saved locally.")
        else:
            logger.error("Authentication failed. Please check your network and credentials in .env")
            sys.exit(1)

    if args.post:
        logger.info(f"Attempting to post to LinkedIn: '{args.post}'")
        # Ensure we are authenticated
        if not client.access_token:
            logger.info("No access token found. Initiating authentication...")
            if not client.authenticate():
                logger.error("Could not authenticate. Aborting post.")
                sys.exit(1)

        success = client.post_content(args.post)
        if success:
            logger.info("Check your LinkedIn profile for the new post!")
        else:
            logger.error("Post failed. Check the logs.")
            sys.exit(1)

    if not args.auth and not args.post:
        parser.print_help()
        logger.info("No action provided. Try running with --auth or --post 'Hello World'")

if __name__ == "__main__":
    main()

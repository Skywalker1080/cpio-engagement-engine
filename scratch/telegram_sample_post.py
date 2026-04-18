import asyncio
import logging
import os
import argparse
from telethon import TelegramClient, functions, types, errors
from src.config import _project_root

# User's env-loaded creds
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("telegram_sample_post")

async def main():
    parser = argparse.ArgumentParser(description="Post a sample message to a Telegram target.")
    parser.add_argument("target", help="The username or link of the channel/group (e.g. CryptoPrismio)")
    parser.add_argument("--topic", default="General", help="The topic name if it's a forum (default: General)")
    args = parser.parse_args()

    if not API_ID or not API_HASH:
        logger.error("Missing credentials in .env (TELEGRAM_API_ID, TELEGRAM_API_HASH).")
        return

    session_path = os.path.join(_project_root, "cpio_user_session")
    client = TelegramClient(session_path, int(API_ID), API_HASH)
    
    await client.connect()
    
    if not await client.is_user_authorized():
        logger.info("Authorizing client (will prompt for code)...")
        await client.send_code_request(PHONE)
        code = input("Enter the code you received on Telegram: ")
        try:
            await client.sign_in(PHONE, code)
        except errors.SessionPasswordNeededError:
            password = input("2-Step Verification enabled. Enter your password: ")
            await client.sign_in(password=password)

    target = args.target
    message = "🚀 Operational Test: Telegram User API Integration Successful.\n\nThis message was sent automatically via the CryptoPrism Engagement Engine."

    try:
        # Resolve target ONLY by searching active chats (dialogs) by Title
        entity = None
        logger.info(f"Searching your active chats for title: '{target}'...")
        
        async for dialog in client.iter_dialogs():
            if dialog.name and dialog.name.lower() == target.lower():
                entity = dialog.entity
                break
            
        if not entity:
            logger.error(f"Could not find target '{target}' in your chats. Make sure you have joined it and the title matches exactly.")
            return

        logger.info(f"Found entity: {entity.title if hasattr(entity, 'title') else getattr(entity, 'username', 'Unknown')}")

        # Check for Topics (Forum)
        reply_to = None
        if getattr(entity, 'forum', False):
            logger.info(f"Target is a Forum. Looking for '{args.topic}' topic...")
            # Fetch topics via messages module
            result = await client(functions.messages.GetForumTopicsRequest(
                peer=entity,
                offset_date=0,
                offset_id=0,
                offset_topic=0,
                limit=100
            ))
            
            for topic in result.topics:
                if hasattr(topic, 'title') and topic.title.lower() == args.topic.lower():
                    reply_to = topic.id
                    logger.info(f"Found topic '{args.topic}' with ID: {reply_to}")
                    break
            
            if not reply_to:
                logger.warning(f"Topic '{args.topic}' not found. Defaulting to general root (ID 1 usually).")
                reply_to = 1

        await client.send_message(entity, message, reply_to=reply_to)
        logger.info(f"Sample post SENT successfully to {target}!")

    except Exception as e:
        logger.error(f"Failed to post: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    # Telethon needs its own loop management if not using client.run_until_disconnected()
    asyncio.run(main())

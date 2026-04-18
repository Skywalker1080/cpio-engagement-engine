"""
Post a reply or message using a Telegram User account (MTProto).
"""

import os
import logging
from telethon import TelegramClient
from src.config import _project_root

# Load creds from env (Note: You may need to add these to src/config.py constants as well)
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")

logger = logging.getLogger("telegram_user_reply")

async def send_telegram_user_reply(chat_id: str, message_text: str, reply_to_msg_id: int = None, client: TelegramClient = None):
    """
    Connects to Telegram as the user and sends a message.
    Accepts an existing client instance to prevent SQLite "database is locked" errors.
    """
    if not API_ID or not API_HASH:
        logger.error("Missing TELEGRAM_API_ID or TELEGRAM_API_HASH in environment.")
        return False

    async def _send(t_client: TelegramClient):
        try:
            # Handle chat names (like 'cointelegraph' or t.me/link)
            entity = await t_client.get_entity(chat_id)
            await t_client.send_message(entity, message_text, reply_to=reply_to_msg_id)
            logger.info(f"Successfully sent Telegram message to {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    if client:
        # Use existing connected client (no 'with' context avoiding lock errors)
        return await _send(client)

    # Session file will be stored in the project root if starting fresh
    session_path = os.path.join(_project_root, "cpio_user_session")
    
    async with TelegramClient(session_path, int(API_ID), API_HASH) as new_client:
        return await _send(new_client)

if __name__ == "__main__":
    # Quick test runner
    import asyncio
    async def test():
        await send_telegram_user_reply("me", "Hello from CryptoPrism Engine!")
    asyncio.run(test())

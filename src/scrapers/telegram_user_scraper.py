"""
Scrape messages from Telegram using the User API (Telethon).
Faster and free compared to cloud scrapers.
"""

import os
import logging
from telethon import TelegramClient
from src.config import _project_root

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")

logger = logging.getLogger("telegram_user_scraper")

async def search_telegram_user_history(keywords: list[str], channels: list[str] = None, limit_per_keyword: int = 10):
    """
    Searches across specified channels or all joined chats for specific keywords using the user account.
    """
    if not API_ID or not API_HASH:
        logger.error("Missing Telegram API credentials.")
        return

    session_path = os.path.join(_project_root, "cpio_user_session")
    
    async with TelegramClient(session_path, int(API_ID), API_HASH) as client:
        # If channels are specified, we search inside them. Otherwise globally (None).
        targets = channels if channels else [None]
        
        for target in targets:
            # Resolve entity if it's a specific channel
            entity = None
            if target:
                try:
                    # First try exact get_entity
                    entity = await client.get_entity(target)
                except Exception:
                    # Fallback to search dialogs for the exact title
                    async for dialog in client.iter_dialogs():
                        if dialog.name and dialog.name.lower() == target.lower():
                            entity = dialog.entity
                            break
                if not entity:
                    logger.warning(f"Could not resolve target channel '{target}', skipping.")
                    continue

            for keyword in keywords:
                target_name = getattr(entity, 'title', target) if entity else "ALL CHATS"
                logger.info(f"Searching in '{target_name}' for keyword: '{keyword}'...")
                
                async for message in client.iter_messages(entity, search=keyword, limit=limit_per_keyword):
                    try:
                        # Attempt to resolve the chat context
                        chat = None
                        if message.chat_id:
                            chat = await message.get_chat()
                        
                        chat_title = getattr(chat, 'title', 'Private/Direct Chat')
                        
                        yield {
                            "text": message.text,
                            "sender_id": str(message.sender_id),
                            "chat_title": chat_title,
                            "chat_id": message.chat_id,
                            "message_id": message.id,
                            "date": message.date.isoformat() if message.date else None,
                            "keyword": keyword,
                            "_client": client
                        }
                    except Exception as e:
                        logger.error(f"Error parsing message: {e}")

if __name__ == "__main__":
    import asyncio
    async def test():
        async for msg in search_telegram_user_history(["bitcoin", "crypto"], limit_per_keyword=2):
            print(f"[{msg['chat_title']}] {msg['text'][:50]}...")
    asyncio.run(test())

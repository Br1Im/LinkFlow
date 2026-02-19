#!/usr/bin/env python3
"""Script to delete webhook for crypto bot"""
import asyncio
from aiogram import Bot
import config

async def delete_webhook():
    bot = Bot(token=config.API_TOKEN)
    try:
        # Get webhook info
        webhook_info = await bot.get_webhook_info()
        print(f"Current webhook: {webhook_info.url}")
        print(f"Pending updates: {webhook_info.pending_update_count}")
        
        # Delete webhook
        result = await bot.delete_webhook(drop_pending_updates=True)
        print(f"Webhook deleted: {result}")
        
        # Verify
        webhook_info = await bot.get_webhook_info()
        print(f"New webhook: {webhook_info.url}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(delete_webhook())

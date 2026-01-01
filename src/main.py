import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot
from src.bot.setup import setup_bot
from src.config import settings
from src.core.Weather import Weather
from src.db.crud import create_db

async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info('db init...')
    create_db()
    logging.info('db created')
    logging.info('bot init...')
    dp = setup_bot()
    bot = Bot(token=settings.BOT_TOKEN)
    logging.info('bot started')
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('bot stopped')

import asyncio
import logging
from aiogram import Bot
from src.bot.setup import setup_bot
from config import settings
from src.db.crud import create_db

async def main():

    logging.basicConfig(level=logging.INFO)
    logging.info('db init...')
    create_db()
    logging.info('db created')
    dp = setup_bot()
    bot = Bot(token=settings.BOT_TOKEN)
    logging.info('bot started')
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('bot stopped')

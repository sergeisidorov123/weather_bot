import asyncio
import logging
from aiogram import Bot
from src.core.Weather import Weather
from src.bot.setup import setup_bot
from config import settings

async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info('bot started')
    dp = setup_bot()
    bot = Bot(token=settings.BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('bot stopped')

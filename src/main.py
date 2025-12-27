import asyncio
import logging
from aiogram import Bot
from src.core.Weather import Weather
from src.bot.setup import setup_bot
from config import settings

async def main():
    w = Weather(38, 56)

    current = w.get_current_weather()

    tomorrow = w.get_weather_for_some_days(5)
    today = w.get_hourly_weather("2025-11-22")
    print(current)
    print(tomorrow.get_weather_data_tomorrow())
    print(tomorrow.get_weather_data_forecast())
    print(today.get_weather_for_today(10, 12))
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

#TODO
# обработка ошибок
# город по кордам
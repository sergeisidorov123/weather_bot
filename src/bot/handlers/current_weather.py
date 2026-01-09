from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import logging

from src.bot.keyboard import get_location, get_main_menu
from src.core.Weather import Weather
from src.db.crud import get_user_by_id

router = Router()
logging.basicConfig(level=logging.INFO)

@router.message(F.text == "Current weather")
@router.message(Command("curweather"))
async def send_current_weather(message: Message, state: FSMContext):
    """Текущая погода для пользователя из бд"""
    await state.clear()
    user_id = message.from_user.id
    user = await get_user_by_id(user_id)
    logging.info(f'User {user_id} choose current weather')
    if user is None:
        await message.answer("First need to send location", reply_markup=get_location())
    else:
        try:
            longitude = user.longitude
            latitude = user.latitude
            w = Weather(longitude, latitude)
            current = w.get_current_weather()
            await message.answer(text=f"{user.city}: \n\nTemp: {current.temperature}°С\n"
                                      f"WindSpeed: {current.windspeed} M/S \n{current.weathercode}")
        except Exception as e:
            logging.error(f"Error getting current weather: {e}")
            await message.answer("Error getting weather data. Please try again.", reply_markup=get_main_menu())

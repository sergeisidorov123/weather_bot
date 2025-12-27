from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from geopy import Nominatim

from src.bot.keyboard import get_main_menu
from src.core.Weather import Weather
from geopy.geocoders import Nominatim

router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    """Bot start reply"""
    user_id = message.from_user.id
    # искать юзера в базе и писать ему его город если найден, иначе что-то типо приветствия
    await message.answer("Weather bot", reply_markup=get_main_menu())


@router.message(F.text == "Current weather")
@router.message(Command("curweather"))
async def current_weather(message: Message):
    """Give current weather to user"""
    user_id = message.from_user.id
    # брать из бд город юзера и в корды пихать
    w = Weather(56.2853, 58.0176)
    geolocator = Nominatim(user_agent='weather_bot')
    location = geolocator.reverse(f"{w.latitude}, {w.longitude}")
    city = location.raw["address"]["city"]
    current = w.get_current_weather()
    await message.answer(text=f"{city}: \n\nТемпература:{current.temperature} \n"
                              f"Скорость ветра:{current.windspeed} \n{current.weathercode}")


#сделать кнопку назад
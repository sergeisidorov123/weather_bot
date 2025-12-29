from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from src.bot.keyboard import get_main_menu, get_location
from src.core.Weather import Weather
from geopy.geocoders import Nominatim
from src.db.crud import insert_user, get_user_by_id

router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    """Bot start reply"""
    user_id = message.from_user.id
    # искать юзера в базе и писать ему его город если найден, иначе что-то типо приветствия
    await message.answer("Weather bot", reply_markup=get_main_menu())


@router.message(F.text == "Current weather")
@router.message(Command("curweather"))
async def send_current_weather(message: Message):
    """Give current weather to user"""
    user_id = message.from_user.id
    user = get_user_by_id(user_id)
    print("user", user)
    if user is None:
        await message.answer("User not found")
    else:
        longitude = user.longitude
        latitude = user.latitude
        w = Weather(longitude, latitude)
        geolocator = Nominatim(user_agent='weather_bot')
        location = geolocator.reverse(f"{w.latitude}, {w.longitude}")
        city = location.raw["address"]["city"]
        current = w.get_current_weather()
        print(current)
        await message.answer(text=f"{city}: \n\nТемпература: {current.temperature} \n"
                                  f"Скорость ветра: {current.windspeed} \n{current.weathercode}")

@router.message(F.text == "Hourly weather")
@router.message(Command("hourlyweather"))
async def send_hourly_weather(message: Message):
    # Добавить выбор часов пользователем
    today_date = datetime.today().date()
    user_id = message.from_user.id
    w = Weather(56.2853, 58.0176)
    geolocator = Nominatim(user_agent='weather_bot')
    location = geolocator.reverse(f"{w.latitude}, {w.longitude}")
    city = location.raw["address"]["city"]
    today = w.get_hourly_weather(today_date)
    hourly = today.get_weather_for_today_by_hours(0,2)
    await message.answer(text=f"{city}")
    for hour in hourly:
        await message.answer(text=f"Время: {hour.time[-4:]}\n\nТемпература:{hour.temperature} \n"
                             f"Скорость ветра:{hour.windspeed} \n{hour.weathercode}")

@router.message(Command("location"))
#название кнопки/команды
async def set_location_command(message: Message):
    """Ask for user location"""
    await message.answer(
        "Отправьте свою геолокацию:",
        reply_markup=get_location()
    )

@router.message(F.location)
async def get_user_location(message: Message):
    """Get user location"""
    #добавлять локу в бд
    location = message.location
    await message.answer(f"{location}")

#Ввод даты
#сделать кнопку назад
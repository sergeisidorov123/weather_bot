from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from .keyboard import get_main_menu, get_location, get_hours_keyboard
from ..core.Weather import Weather
from ..db.crud import insert_user, get_user_by_id
from .utils import HourChoose


router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    """Bot start reply"""
    user_id = message.from_user.id
    user = get_user_by_id(user_id)
    await message.delete()
    if user is None:
        await message.answer("Not founded in db", reply_markup=get_location())
    else:
        await message.answer(f"Choose:", reply_markup=get_main_menu())


@router.message(F.text == "Current weather")
@router.message(Command("curweather"))
async def send_current_weather(message: Message):
    """Give current weather to user in city from db"""
    user_id = message.from_user.id
    user = get_user_by_id(user_id)
    await message.delete()
    if user is None:
        await message.answer("First need to send location", reply_markup=get_location())
    else:
        longitude = user.longitude
        latitude = user.latitude
        w = Weather(longitude, latitude)
        current = w.get_current_weather()
        await message.answer(text=f"{user.city}: \n\nTemp: {current.temperature}°С\n"
                                  f"WindSpeed: {current.windspeed} M/S \n{current.weathercode}")


@router.message(F.text == "Hourly weather")
@router.message(Command("hourlyweather"))
async def start_hourly_weather_selection(message: Message, state: FSMContext):
    await message.delete()
    await message.answer("Choose start hour:", reply_markup=get_hours_keyboard('start'))
    await state.set_state(HourChoose.waiting_start_hour)


@router.message(HourChoose.waiting_start_hour)
async def get_start_hour(message: Message, state: FSMContext):
    if not message.text.isdigit() or not (0 <= int(message.text) <= 24):
        await message.answer("Choose correctly")
        return

    await state.update_data(start=int(message.text))
    await state.set_state(HourChoose.waiting_end_hour)
    await message.delete()
    await message.answer(
        f"Start: {message.text}:00\n\nChoose end hour:",
        reply_markup=get_hours_keyboard('end')
    )


@router.message(HourChoose.waiting_end_hour)
async def get_end_hour(message: Message, state: FSMContext):
    if not message.text.isdigit() or not (0 <= int(message.text) <= 24):
        await message.answer("Choose correctly")
        return

    data = await state.get_data()
    start_hour = data['start']
    end_hour = int(message.text)
    await state.update_data(end=end_hour)
    await message.delete()
    if end_hour <= start_hour:
        await message.answer("End hour should be lower than start hour")
        return
    await state.set_state(HourChoose.weather_forecast)
    await send_hourly_weather(message, state)


async def send_hourly_weather(message: Message, state: FSMContext):
    """Give hourly weather to user in city from db"""
    data = await state.get_data()
    start_hour = data['start']
    end_hour = (data['end'] + 1)
    today_date = datetime.today().date()
    user_id = message.from_user.id
    user = get_user_by_id(user_id)
    if user is None:
        await message.answer("First need to send location", reply_markup=get_location())
    else:
        longitude = user.longitude
        latitude = user.latitude
        w = Weather(longitude, latitude)
        today = w.get_hourly_weather(today_date)
        hourly = today.get_weather_for_today_by_hours(start_hour,end_hour)
        await message.answer(text = f"Hourly weather")
        await message.answer(text=f"{user.city}")
        for hour in hourly:
            await message.answer(text=f"Time: {hour.time[-5:]}\n\nTemp:{hour.temperature}°С\n"
                                 f"Wind speed:{hour.windspeed} M/S \n{hour.weathercode}", reply_markup=get_main_menu())


@router.message(F.location)
async def add_user_to_db(message: Message):
    """Add user to db"""
    location = message.location
    insert_user(message.from_user.id, location)
    await message.delete()
    await message.answer(f"Location get successfully", reply_markup=get_main_menu())


@router.message(F.text == "Cancel")
async def return_to_main_menu(message: Message):
    await message.delete()
    await message.answer("Return to the main menu", reply_markup=get_main_menu())

#Ввод даты
#Обработка ошибок
#Разделить ответственность
#ошибки ловить
#
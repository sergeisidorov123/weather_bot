from datetime import datetime, timedelta
from typing import Union

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import logging

from src.bot.handlers.utils import HourChoose, is_valid_date, is_within_forecast_range, DayChoose
from src.bot.keyboard import get_location, get_main_menu, get_hours_keyboard, get_daily_keyboard, \
    choose_path_of_daily_keyboard
from src.core.Weather import Weather
from src.db.crud import get_user_by_id

router = Router()
logging.basicConfig(level=logging.INFO)

@router.message(F.text == "Daily weather")
async def daily_weather_selection(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Choose", reply_markup=choose_path_of_daily_keyboard())


@router.message(F.text == "Get weather for a day")
async def daily_weather_selection_day(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(DayChoose.waiting_day)
    await message.answer("Choose day from the buttons below:", reply_markup=get_daily_keyboard())

@router.message(DayChoose.waiting_day)
async def send_daily_weather_for_a_day(message: Message, state: FSMContext):
    try:
        user_id = message.from_user.id
        day_input = message.text.strip()

        if day_input == "Now":
            day = datetime.today().date()
        else:
            if not is_valid_date(day_input):
                await message.answer("Invalid date format. Please use YYYY-MM-DD")
                return

            day = datetime.strptime(day_input, "%Y-%m-%d").date()

            if not is_within_forecast_range(day):
                await message.answer("Date should be within 7 days from today")
                return

        await send_daily_weather(message, day, day, user_id)
        await state.clear()
    except Exception as e:
        logging.error(f"Error in daily weather selection: {e}")
        await message.answer("An error occurred. Please try again.")
        await state.clear()


@router.callback_query(F.data.startswith("day_"), DayChoose.waiting_day)
async def handle_date_selection_for_daily(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора даты из клавиатуры для дневного прогноза"""
    try:
        data = callback.data.split("_")

        if len(data) != 2:
            await callback.answer("Invalid data format")
            return

        day_value = data[1]

        if day_value == "cancel":
            await callback.message.delete()
            await callback.answer("Cancelled")
            await state.clear()
            return
        elif day_value == "now":
            day = datetime.today().date()
        else:
            if not is_valid_date(day_value):
                await callback.answer("Invalid date format")
                return

            day = datetime.strptime(day_value, "%Y-%m-%d").date()

            if not is_within_forecast_range(day):
                await callback.answer("Date should be within 7 days from today")
                return

        await callback.message.delete()

        user_id = callback.from_user.id
        user = await get_user_by_id(user_id)
        if user is None:
            await callback.bot.send_message(
                chat_id=callback.message.chat.id,
                text="First need to send location",
                reply_markup=get_location()
            )
            await state.clear()
            return

        if user.longitude is None or user.latitude is None:
            await callback.message.answer("Location data is missing. Please send your location again.",
                                          reply_markup=get_location())
            await state.clear()
            return

        await send_daily_weather(callback.message, day, day, user_id)
        await state.clear()
        await callback.answer()

    except Exception as e:
        logging.error(f"Error in date selection for daily: {e}", exc_info=True)
        await callback.answer("An error occurred")
        await state.clear()


@router.message(F.text == "Get weather for a week")
async def send_daily_weather_for_a_week(message: Message):
    try:
        start_day = datetime.today().date()
        end_day = start_day + timedelta(days=6)

        if not is_within_forecast_range(end_day, start_day):
            await message.answer("Cannot get forecast for more than 7 days")
            return

        await send_daily_weather(message, start_day, end_day)
    except Exception as e:
        logging.error(f"Error getting weekly weather: {e}")
        await message.answer("Error getting weather data. Please try again.")


async def send_daily_weather(message: Message, start_day: datetime.date, end_day: datetime.date, user_id: int | None = None):
    if user_id is None:
        user_id = message.from_user.id

    user = await get_user_by_id(user_id)
    logging.info(f'User {user_id} choose daily weather for {start_day} to {end_day}')
    print(user)
    print(user.longitude, user.latitude)
    if user is None:
        await message.answer("First need to send location", reply_markup=get_location())
        return

    if user.longitude is None or user.latitude is None or user.city is None:
        await message.answer("Location data is incomplete. Please update your location.", reply_markup=get_location())
        return

    try:
        delta_days = (end_day - start_day).days
        if delta_days > 6:
            await message.answer("Cannot get forecast for more than 7 days")
            return

        longitude = user.longitude
        latitude = user.latitude
        w = Weather(longitude, latitude)
        forecast = w.get_weather_for_some_days(start_day, end_day)
        day_forecast = forecast.get_weather_data_forecast()

        await message.answer(text=f"{user.city} ({start_day} to {end_day}):")

        if not day_forecast:
            await message.answer("No weather data available")
        else:
            for day in day_forecast:
                await message.answer(text=f"Day: {day.time}\n\n"
                                          f"Temp max: {day.temperature_2m_max}°С\n"
                                          f"Temp min: {day.temperature_2m_min}°С\n"
                                          f"Max wind speed: {day.wind_speed_10m_max} M/S \n"
                                          f"{day.weathercode}")

        await message.answer("Choose:", reply_markup=get_main_menu())
    except Exception as e:
        logging.error(f"Error in send_daily_weather: {e}")
        await message.answer("Error getting weather data. Please try again.", reply_markup=get_main_menu())
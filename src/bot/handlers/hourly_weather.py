from datetime import datetime
from typing import Union

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import logging

from src.bot.handlers.utils import HourChoose, is_valid_date, is_within_forecast_range
from src.bot.keyboard import get_location, get_main_menu, get_hours_keyboard, get_daily_keyboard
from src.core.Weather import Weather
from src.db.crud import get_user_by_id

router = Router()
logging.basicConfig(level=logging.INFO)

@router.callback_query(F.data.startswith("hours_"))
async def handle_hours_pagination(callback: CallbackQuery, state: FSMContext):
    """Пагинация для выбора промежутка часового"""
    try:
        parts = callback.data.split("_")

        if len(parts) < 4:
            await callback.answer("Error format")
            return

        action = parts[1]
        mode = parts[2]
        current_page = int(parts[3])

        if action == "next":
            new_page = current_page + 1
        elif action == "prev":
            new_page = current_page - 1
        else:
            await callback.answer("Unknown command")
            return

        if new_page < 0:
            await callback.answer()
            return

        hours_per_page = 8
        if new_page * hours_per_page >= 24:
            await callback.answer()
            return

        await callback.answer()

        await callback.message.edit_reply_markup(
            reply_markup=get_hours_keyboard(mode=mode, page=new_page)
        )

    except Exception as e:
        logging.error(f"Error in pagination: {e}")
        await callback.answer("An error occurred")


@router.callback_query(F.data.startswith("hour_"))
async def handle_hour_selection(callback: CallbackQuery, state: FSMContext):
    try:
        data = callback.data.split("_")

        if data[1] == "cancel":
            await callback.message.delete()
            await callback.answer("Cancelled")
            await state.clear()
            return

        mode = data[1]
        hour_value = data[2]
        current_state = await state.get_state()

        if current_state == HourChoose.waiting_start_hour.state:
            await state.update_data(start_hour=hour_value)

            data = await state.get_data()
            date_str = data.get('hourly_date', 'Now')
            if date_str == "Now":
                selected_date = datetime.today().date()
            else:
                selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()

            await callback.message.edit_text(f"Choose end hour for {selected_date}:")
            await callback.message.edit_reply_markup(
                reply_markup=get_hours_keyboard('end')
            )
            await state.set_state(HourChoose.waiting_end_hour)

        elif current_state == HourChoose.waiting_end_hour.state:
            await state.update_data(end_hour=hour_value)
            data = await state.get_data()

            start_hour = data.get('start_hour')
            end_hour = hour_value
            date_str = data.get('hourly_date')

            if not start_hour or not end_hour:
                await callback.message.edit_text("Error: Missing start or end hour")
                await callback.answer()
                return

            if start_hour.isdigit() and end_hour.isdigit():
                start_hour_int = int(start_hour)
                end_hour_int = int(end_hour)

                if end_hour_int <= start_hour_int:
                    await callback.message.edit_text("End hour should be greater than start hour")
                    await callback.answer()
                    return

            user_id = callback.from_user.id
            user = await get_user_by_id(user_id)

            if user is None:
                await callback.message.edit_text("First need to send location", reply_markup=get_location())
            else:
                await callback.message.delete()

                await callback.answer(f"Selected: {start_hour}:00 - {end_hour}:00")

                if date_str == "Now":
                    selected_date = datetime.today().date()
                else:
                    selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()

                await send_hourly_weather_for_selected_hours(
                    callback.message,
                    user,
                    start_hour,
                    end_hour,
                    selected_date
                )

            await state.clear()

        await callback.answer()
    except Exception as e:
        logging.error(f"Error in hour selection: {e}")
        await callback.answer("An error occurred")


@router.message(F.text == "Hourly weather")
@router.message(Command("hourlyweather"))
async def start_hourly_weather_selection(message: Message, state: FSMContext):
    """Начало выбора почасового прогноза с клавиатурой выбора даты"""
    await state.clear()
    await message.answer("Choose date for hourly forecast:", reply_markup=get_daily_keyboard())
    await state.set_state(HourChoose.waiting_date_for_hourly)


@router.callback_query(F.data.startswith("day_"), HourChoose.waiting_date_for_hourly)
async def handle_date_selection_for_hourly(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора даты из клавиатуры для почасового прогноза"""
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
            selected_date = datetime.today().date()
            date_str = "Now"
        else:
            if not is_valid_date(day_value):
                await callback.answer("Invalid date format")
                return

            selected_date = datetime.strptime(day_value, "%Y-%m-%d").date()

            if not is_within_forecast_range(selected_date):
                await callback.answer("Date should be within 7 days from today")
                return

            date_str = day_value

        await state.update_data(hourly_date=date_str)

        await callback.message.delete()

        await callback.message.answer(f"Date selected: {selected_date}\nChoose start hour:",
                                      reply_markup=get_hours_keyboard('start'))
        await state.set_state(HourChoose.waiting_start_hour)
        await callback.answer()

    except Exception as e:
        logging.error(f"Error in date selection for hourly: {e}")
        await callback.answer("An error occurred")


@router.message(HourChoose.waiting_date_for_hourly)
async def handle_date_input_for_hourly(message: Message, state: FSMContext):
    """Обработка текстового ввода даты для почасового прогноза (альтернатива клавиатуре)"""
    date_input = message.text.strip()

    if date_input.lower() == "now":
        selected_date = datetime.today().date()
        date_str = "Now"
    else:
        if not is_valid_date(date_input):
            await message.answer("Invalid date format. Please use YYYY-MM-DD or type 'Now'")
            return

        selected_date = datetime.strptime(date_input, "%Y-%m-%d").date()

        if not is_within_forecast_range(selected_date):
            await message.answer("Date should be within 7 days from today")
            return

        date_str = date_input

    await state.update_data(hourly_date=date_str)
    await message.answer(f"Date selected: {selected_date}\nChoose start hour:",
                         reply_markup=get_hours_keyboard('start'))
    await state.set_state(HourChoose.waiting_start_hour)


@router.message(HourChoose.waiting_start_hour)
async def get_start_hour(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user_by_id(user_id)
    if user is None:
        await message.answer("First need to send location", reply_markup=get_location())
        await state.clear()
        return

    data = await state.get_data()
    date_str = data.get('hourly_date', 'Now')

    if date_str == "Now":
        selected_date = datetime.today().date()
    else:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    if not message.text.isdigit() or not (0 <= int(message.text) < 24):
        await message.answer("Please enter a valid hour (0-23)")
        return

    start_hour = int(message.text)
    await state.update_data(start=start_hour, user=user)

    await message.answer(
        f"Date: {selected_date}\nStart: {message.text}:00\n\nChoose end hour:",
        reply_markup=get_hours_keyboard('end')
    )
    await state.set_state(HourChoose.waiting_end_hour)


@router.message(HourChoose.waiting_end_hour)
async def get_end_hour(message: Message, state: FSMContext):
    if not message.text.isdigit() or not (0 <= int(message.text) < 24):
        await message.answer("Please enter a valid hour (0-23)")
        return

    data = await state.get_data()
    start_hour = data['start']
    end_hour = int(message.text)

    if end_hour <= start_hour:
        await message.answer("End hour should be greater than start hour")
        return

    await state.update_data(end=end_hour)

    date_str = data.get('hourly_date', 'Now')
    if date_str == "Now":
        selected_date = datetime.today().date()
    else:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    await send_hourly_weather_for_selected_hours(message, state, selected_date)


async def send_hourly_weather_for_selected_hours(
        message: Union[Message, CallbackQuery],
        state_or_user: Union[FSMContext, object],
        start_hour: int = None,
        end_hour: int = None,
        selected_date: datetime.date = None
):
    """Вывод почасовой погоды для выбранных часов"""
    try:
        if isinstance(state_or_user, FSMContext):
            data = await state_or_user.get_data()
            start_hour = data['start']
            end_hour = data['end']
            user = data['user']

            date_str = data.get('hourly_date', 'Now')
            if date_str == "Now":
                selected_date = datetime.today().date()
            else:
                selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        else:
            user = state_or_user
            if selected_date is None:
                selected_date = datetime.today().date()

        w = Weather(user.longitude, user.latitude)
        date_forecast = w.get_hourly_weather(selected_date)

        if end_hour == 0 or (isinstance(end_hour, str) and end_hour == "0"):
            end_hour_int = 24
        else:
            end_hour_int = int(end_hour) if isinstance(end_hour, str) else end_hour

        start_hour_int = int(start_hour) if isinstance(start_hour, str) else start_hour

        hourly = date_forecast.get_weather_for_today_by_hours(start_hour_int, end_hour_int)

        if isinstance(message, CallbackQuery):
            msg_obj = message.message
        else:
            msg_obj = message

        await msg_obj.answer(text=f"{user.city} on {selected_date}:")

        if not hourly:
            await msg_obj.answer("No weather data available for selected hours")
        else:
            for hour in hourly:
                await msg_obj.answer(
                    text=f"Time: {hour.time[-5:]}\n\n"
                         f"Temp: {hour.temperature}°С\n"
                         f"Wind speed: {hour.windspeed} M/S \n"
                         f"{hour.weathercode}"
                )

        await msg_obj.answer("Choose:", reply_markup=get_main_menu())

    except Exception as e:
        logging.error(f"Error showing hourly weather: {e}")
        error_msg = "Error showing weather. Please try again."
        if isinstance(message, CallbackQuery):
            await message.message.answer(error_msg, reply_markup=get_main_menu())
        else:
            await message.answer(error_msg, reply_markup=get_main_menu())
    finally:
        if isinstance(state_or_user, FSMContext):
            await state_or_user.clear()

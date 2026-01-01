import logging
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from .keyboard import get_main_menu, get_location, get_hours_keyboard, get_daily_keyboard, choose_path_of_daily_keyboard
from ..core.Weather import Weather
from ..db.crud import insert_user, get_user_by_id, city_change
from .utils import HourChoose, DayChoose, CityChoose

logging.basicConfig(level=logging.INFO)
router = Router()

@router.message(CommandStart())
async def start_command(message: Message):
    """Bot start reply"""
    user_id = message.from_user.id
    user = await get_user_by_id(user_id)
    if user is None:
        logging.info(f'User {user_id} not founded in db')
        await message.answer("Not founded in db", reply_markup=get_location())
    else:
        logging.info(f'User {user_id} started')
        await message.answer(f"Choose:", reply_markup=get_main_menu())


@router.message(F.text == "Current weather")
@router.message(Command("curweather"))
async def send_current_weather(message: Message):
    """Give current weather to user in city from db"""
    user_id = message.from_user.id
    user = await get_user_by_id(user_id)
    logging.info(f'User {user_id} choose current weather')
    if user is None:
        await message.answer("First need to send location", reply_markup=get_location())
    else:
        longitude = user.longitude
        latitude = user.latitude
        w = Weather(longitude, latitude)
        current = w.get_current_weather()
        await message.answer(text=f"{user.city}: \n\nTemp: {current.temperature}°С\n"
                                  f"WindSpeed: {current.windspeed} M/S \n{current.weathercode}")


@router.callback_query(F.data.startswith("hours_"))
async def handle_hours_pagination(callback: CallbackQuery, state: FSMContext):
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
            await callback.answer("Неизвестное действие")
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


@router.callback_query(F.data.startswith("hour_"))
async def handle_hour_selection(callback: CallbackQuery, state: FSMContext):
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
        await callback.message.edit_text("Choose end hour:")
        await callback.message.edit_reply_markup(
            reply_markup=get_hours_keyboard('end')
        )
        await state.set_state(HourChoose.waiting_end_hour)
    elif current_state == HourChoose.waiting_end_hour.state:
        await state.update_data(end_hour=hour_value)
        data = await state.get_data()

        start_hour = data.get('start_hour')
        end_hour = hour_value


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

            await send_hourly_weather_for_selected_hours(
                callback.message,
                user,
                start_hour,
                end_hour
            )

        await state.clear()

    await callback.answer()

@router.message(F.text == "Hourly weather")
@router.message(Command("hourlyweather"))
async def start_hourly_weather_selection(message: Message, state: FSMContext):
    await message.answer("Choose start hour:", reply_markup=get_hours_keyboard('start'))
    await state.set_state(HourChoose.waiting_start_hour)


@router.message(HourChoose.waiting_start_hour)
async def get_start_hour(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user_by_id(user_id)
    if user is None:
        await message.answer("First need to send location", reply_markup=get_location())
    else:
        if not message.text.isdigit() or not (0 <= int(message.text) <= 24):
            await message.answer("Choose correctly")
            return

        await state.update_data(start=int(message.text))
        await state.set_state(HourChoose.waiting_end_hour)
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
    if end_hour <= start_hour:
        await message.answer("End hour should be lower than start hour")
        return
    await send_hourly_weather_for_selected_hours(message, state)
    await state.clear()


async def send_hourly_weather_for_selected_hours(message: Message, user, start_hour_str: str, end_hour_str: str):
    """Give hourly weather for selected hours"""
    try:
        start_hour = int(start_hour_str)
        end_hour = int(end_hour_str)

        today_date = datetime.today().date()

        w = Weather(user.longitude, user.latitude)
        today = w.get_hourly_weather(today_date)
        hourly = today.get_weather_for_today_by_hours(start_hour, end_hour)

        await message.answer(text=f"{user.city}:")

        for hour in hourly:
            await message.answer(
                text=f"Time: {hour.time[-5:]}\n\n"
                     f"Temp: {hour.temperature}°С\n"
                     f"Wind speed: {hour.windspeed} M/S \n"
                     f"{hour.weathercode}"
            )

        await message.answer("Choose:", reply_markup=get_main_menu())

    except Exception as e:
        logging.error(f"Error showing hourly weather: {e}")
        await message.answer("Error showing weather. Please try again.", reply_markup=get_main_menu())


@router.message(F.location)
async def add_user_to_db_via_loc(message: Message):
    """Add user to db"""
    location = message.location
    await insert_user(message.from_user.id, location)
    logging.info(f'User {message.user_id} send location: {location}')
    await message.answer(f"Location get successfully", reply_markup=get_main_menu())


@router.message(F.text == "Cancel")
async def return_to_main_menu(message: Message):
    await message.answer("Return to the main menu", reply_markup=get_main_menu())


@router.message(F.text == "Daily weather")
async def daily_weather_selection(message: Message):
    await message.answer("Choose", reply_markup=choose_path_of_daily_keyboard())

@router.message(F.text == "Get weather for a day")
async def daily_weather_selection(message: Message, state: FSMContext):
    await message.answer("Choose day", reply_markup=get_daily_keyboard())
    await state.set_state(DayChoose.waiting_day)

@router.message(DayChoose.waiting_day)
async def send_daily_weather_for_a_day(message: Message, state: FSMContext):
    day = message.text
    if day == "Now":
        day = datetime.today().date()
    #Валидировать
    await send_daily_weather(message, day, day)
    await state.clear()


@router.message(F.text == "Get weather for a week")
async def send_daily_weather_for_a_week(message: Message):
    start_day = datetime.today().date()
    end_day = start_day + timedelta(days=7)
    await send_daily_weather(message, start_day, end_day)

async def send_daily_weather(message: Message, start_day, end_day):
    user_id = message.from_user.id
    user = await get_user_by_id(user_id)
    logging.info(f'User {user_id} choose daily weather for a day')
    if user is None:
        await message.answer("First need to send location", reply_markup=get_location())
    else:
        longitude = user.longitude
        latitude = user.latitude
        w = Weather(longitude, latitude)
        forecast = w.get_weather_for_some_days(start_day, end_day)
        day_forecast = forecast.get_weather_data_forecast()
        await message.answer(text=f"{user.city}")
        for day in day_forecast:
            await message.answer(text=f"Day: {day.time}\n\n"
                                      f"Temp max:{day.temperature_2m_max}°С\n"
                                      f"Temp min:{day.temperature_2m_min}°С\n"
                                      f"Max wind speed:{day.wind_speed_10m_max} M/S \n"
                                      f"{day.weathercode}",
                                 reply_markup=get_main_menu())


@router.message(F.text == "Pick town")
async def send_daily_weather_for_today(message: Message, state: FSMContext):
    await message.answer("Send location or enter city name", reply_markup=get_location())
    await state.set_state(CityChoose.waiting_city_name)

@router.message(CityChoose.waiting_city_name)
async def add_user_to_db_via_city_name(message: Message, state: FSMContext):
    await city_change(message.from_user.id, message)
    await message.answer(f"Location get successfully", reply_markup=get_main_menu())
    await state.clear()



#Ввод даты на почасовой
#Обработка ошибок
#Разделить ответственность
#ошибки ловить
#Уведомления о погоде на завтра в тайминг выбранный пользователем
#в часах енд клавиатуру брать от старта
#в погоде по дням распределить для предыдущих дней и следующих
#огран по часам и по дням(7 дней макс)
# типы в функциях
#обрабатывать now и end в hourly
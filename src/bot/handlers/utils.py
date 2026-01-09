from datetime import datetime
from aiogram.types import Message
from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from src.bot.keyboard import get_main_menu, get_location


class HourChoose(StatesGroup):
    waiting_start_hour = State()
    waiting_end_hour = State()
    waiting_date_for_hourly = State()

class DayChoose(StatesGroup):
    waiting_day = State()

class CityChoose(StatesGroup):
    waiting_city_name = State()


def is_valid_date(date_str: str) -> bool:
    """Проверяет, является ли строка валидной датой в формате YYYY-MM-DD"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_within_forecast_range(date: datetime.date, reference_date: datetime.date = None) -> bool:
    """Проверяет, находится ли дата в пределах 7 дней от reference_date"""
    if reference_date is None:
        reference_date = datetime.today().date()

    delta = (date - reference_date).days
    return -7 <= delta <= 7


router = Router()

@router.message(F.text == "Cancel")
async def return_to_main_menu(message: Message):
    await message.answer("Return to the main menu", reply_markup=get_main_menu())

@router.message(F.text == "Pick town")
async def pick_town(message: Message, state: FSMContext):
    """Смена города"""
    await message.answer("Send location or enter city name", reply_markup=get_location())
    await state.set_state(CityChoose.waiting_city_name)
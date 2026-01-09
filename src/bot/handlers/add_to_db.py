from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
import logging

from src.bot.handlers.utils import CityChoose
from src.bot.keyboard import get_main_menu
from src.db.crud import city_change_by_location, city_change_by_name

router = Router()
logging.basicConfig(level=logging.INFO)

@router.message(F.location)
async def add_user_to_db_via_loc(message: Message):
    """Добавление в бд"""
    try:
        await city_change_by_location(message.from_user.id, message)
        await message.answer("Location set successfully", reply_markup=get_main_menu())
    except Exception as e:
        logging.error(f"Error adding user via location: {e}")
        await message.answer("Error saving location. Please try again.")


@router.message(CityChoose.waiting_city_name)
async def add_user_to_db_via_city_name(message: Message, state: FSMContext):
    if message.text in ["Get weather for a day", "Hourly weather", "Current weather", "Daily weather"]:
        await state.clear()
        return

    try:
        await city_change_by_name(message.from_user.id, message.text)
        await message.answer("Location set successfully", reply_markup=get_main_menu())
        await state.clear()
    except ValueError:
        await message.answer("City not found. Try again.")
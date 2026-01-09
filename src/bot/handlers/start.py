from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
import logging

from src.bot.keyboard import get_location, get_main_menu
from src.db.crud import get_user_by_id

router = Router()
logging.basicConfig(level=logging.INFO)

@router.message(CommandStart())
async def start_command(message: Message):
    """Обработка старта"""
    user_id = message.from_user.id
    user = await get_user_by_id(user_id)
    if user is None:
        logging.info(f'User {user_id} not founded in db')
        await message.answer("Not founded in db", reply_markup=get_location())
    else:
        logging.info(f'User {user_id} started')
        await message.answer(f"Choose:", reply_markup=get_main_menu())
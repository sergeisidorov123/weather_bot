from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from src.bot.handlers import router


def setup_bot() -> Dispatcher:
    """Настройка и возврат диспетчера"""
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(router)

    return dp
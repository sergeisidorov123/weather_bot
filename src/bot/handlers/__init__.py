from aiogram import Router
from .add_to_db import router as db_router
from .current_weather import router as current_router
from .daily_weather import router as daily_router
from .hourly_weather import router as hourly_router
from .start import router as start_router
from .utils import router as util_router


main_router = Router()


main_router.include_routers(
    db_router,
    current_router,
    daily_router,
    hourly_router,
    start_router,
    util_router
)
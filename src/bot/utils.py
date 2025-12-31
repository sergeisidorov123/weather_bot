from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

class HourChoose(StatesGroup):
    waiting_start_hour = State()
    waiting_end_hour = State()
    weather_forecast = State()
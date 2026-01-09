from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

class HourChoose(StatesGroup):
    waiting_start_hour = State()
    waiting_end_hour = State()
    waiting_date_for_hourly = State()

class DayChoose(StatesGroup):
    waiting_day = State()

class CityChoose(StatesGroup):
    waiting_city_name = State()
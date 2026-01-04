from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from datetime import datetime, timedelta


def get_main_menu() -> ReplyKeyboardMarkup:
    """Bot main menu"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text = 'Current weather')], [KeyboardButton(text = 'Hourly weather')],
            [KeyboardButton(text = 'Daily weather')], [KeyboardButton(text = 'Settings')],
            [KeyboardButton(text = 'Pick town')]
        ],
        resize_keyboard=True,
        input_field_placeholder="Choose"
    )

def get_location() -> ReplyKeyboardMarkup:
    """Get location keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Send geolocation", request_location=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def get_hours_keyboard(mode: str = 'any', page: int = 0):
    """
    Get keyboard to pick hours
    :param page:
    :param mode:
    'any' - for choose anytime
    'start' - for choose start time
    'end' - for choose end time
    """

    builder = InlineKeyboardBuilder()

    hours_per_page = 8
    start_hour = page * hours_per_page
    end_hour = start_hour + hours_per_page

    for hour in range(start_hour, end_hour):
        if hour < 24:
            builder.add(InlineKeyboardButton(
                text=str(hour),
                callback_data=f"hour_{mode}_{hour}"
            ))

    builder.adjust(4)

    nav_buttons = []

    if page > 0:
        nav_buttons.append(InlineKeyboardButton(
            text="⬅️",
            callback_data=f"hours_prev_{mode}_{page}"
        ))

    if end_hour < 24:
        nav_buttons.append(InlineKeyboardButton(
            text="➡️",
            callback_data=f"hours_next_{mode}_{page}"
        ))

    if nav_buttons:
        builder.row(*nav_buttons)

    if mode == 'start':
        builder.row(InlineKeyboardButton(
            text="Now",
            callback_data=f"hour_{mode}_now"
        ))
    elif mode == 'end':
        builder.row(InlineKeyboardButton(
            text="To the end of the day",
            callback_data=f"hour_{mode}_end"
        ))

    builder.row(InlineKeyboardButton(
        text="Cancel",
        callback_data=f"hour_cancel"
    ))

    return builder.as_markup()

def get_daily_keyboard(mode: str = 'any'):
    builder = ReplyKeyboardBuilder()
    current_date = datetime.today().date()
    for i in range(8, 1, -1):
        builder.add(KeyboardButton(
            text=str(current_date - timedelta(i)),
        ))
    builder.add(KeyboardButton(text="Now"))
    for i in range(1,8):
        builder.add(KeyboardButton(
            text=str(current_date + timedelta(i)),
        ))

    return builder.as_markup(resize_keyboard=True)

def choose_path_of_daily_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Get weather for a day')],
            [KeyboardButton(text='Get weather for a week')]
        ],
        resize_keyboard=True,
        input_field_placeholder="Choose"
    )

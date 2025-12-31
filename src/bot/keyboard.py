from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder


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

def get_hours_keyboard(mode: str = 'any'):
    """
    Get keyboard to pick hours
    :param mode:
    'any' - for choose anytime
    'start' - for choose start time
    'end' - for choose end time
    """

    builder = ReplyKeyboardBuilder()
    for i in range(24):
        builder.add(KeyboardButton(
            text=str(i),
            callback_data=f"number_{i}"
        ))

    builder.adjust(5, 5, 5, 5, 5)

    if mode == 'start':
        builder.row(KeyboardButton(text="Now"))
    elif mode == 'end':
        builder.row(KeyboardButton(text="To the end of the day"))

    builder.row(KeyboardButton(text="Cancel"))

    return builder.as_markup(resize_keyboard=True)

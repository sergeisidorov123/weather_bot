from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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
            [KeyboardButton(text="📍 Отправить местоположение", request_location=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard
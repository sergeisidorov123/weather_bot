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
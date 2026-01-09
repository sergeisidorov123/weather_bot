from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from datetime import datetime, timedelta


def get_main_menu() -> ReplyKeyboardMarkup:
    """Bot main menu"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Current weather')], [KeyboardButton(text='Hourly weather')],
            [KeyboardButton(text='Daily weather')], [KeyboardButton(text='Settings')],
            [KeyboardButton(text='Pick town')]
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


def get_hours_keyboard(mode: str = 'any', page: int = 0, start_hour: int = None):
    """
    Get keyboard to pick hours
    :param page:
    :param mode:
    'any' - for choose anytime
    'start' - for choose start time
    'end' - for choose end time
    :param start_hour: Only for 'end' mode - ограничивает выбор часов
    """

    builder = InlineKeyboardBuilder()

    hours_per_page = 8
    start_hour_page = page * hours_per_page
    end_hour_page = start_hour_page + hours_per_page

    for hour in range(start_hour_page, end_hour_page):
        if hour < 24:
            if mode == 'end' and start_hour is not None:
                if hour <= start_hour:
                    continue

            hour_text = str(hour)
            builder.add(InlineKeyboardButton(
                text=hour_text,
                callback_data=f"hour_{mode}_{hour}"
            ))

    builder.adjust(4)

    nav_buttons = []

    if page > 0:
        nav_buttons.append(InlineKeyboardButton(
            text="⬅️",
            callback_data=f"hours_prev_{mode}_{page}"
        ))

    if end_hour_page < 24:
        if mode == 'end' and start_hour is not None:
            has_next_page = False
            for hour in range(end_hour_page, min(end_hour_page + hours_per_page, 24)):
                if hour > start_hour:
                    has_next_page = True
                    break
            if has_next_page:
                nav_buttons.append(InlineKeyboardButton(
                    text="➡️",
                    callback_data=f"hours_next_{mode}_{page}"
                ))
        else:
            nav_buttons.append(InlineKeyboardButton(
                text="➡️",
                callback_data=f"hours_next_{mode}_{page}"
            ))

    if nav_buttons:
        builder.row(*nav_buttons)

    special_buttons = []
    if mode == 'start':
        special_buttons.append(InlineKeyboardButton(
            text="Now",
            callback_data=f"hour_{mode}_now"
        ))
    elif mode == 'end':
        if start_hour is not None and start_hour < 23:
            special_buttons.append(InlineKeyboardButton(
                text="To the end of the day",
                callback_data=f"hour_{mode}_end"
            ))

    if special_buttons:
        builder.row(*special_buttons)

    builder.row(InlineKeyboardButton(
        text="Cancel",
        callback_data=f"hour_cancel"
    ))

    return builder.as_markup()


def get_daily_keyboard(mode: str = 'any'):
    """Get keyboard for daily weather selection"""
    builder = InlineKeyboardBuilder()

    current_date = datetime.today().date()

    for i in range(7, 0, -1):
        date = current_date - timedelta(days=i)
        builder.add(InlineKeyboardButton(
            text=str(date),
            callback_data=f"day_{date}"
        ))

    builder.add(InlineKeyboardButton(
        text="Today",
        callback_data=f"day_now"
    ))

    for i in range(1, 8):
        date = current_date + timedelta(days=i)
        builder.add(InlineKeyboardButton(
            text=str(date),
            callback_data=f"day_{date}"
        ))

    builder.adjust(3)

    builder.row(InlineKeyboardButton(
        text="Cancel",
        callback_data=f"day_cancel"
    ))

    return builder.as_markup()


def choose_path_of_daily_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Get weather for a day')],
            [KeyboardButton(text='Get weather for a week')]
        ],
        resize_keyboard=True,
        input_field_placeholder="Choose"
    )
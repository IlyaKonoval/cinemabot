from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Поиск фильма")],
            [KeyboardButton(text="История"), KeyboardButton(text="Статистика")]
        ],
        resize_keyboard=True
    )
    return keyboard

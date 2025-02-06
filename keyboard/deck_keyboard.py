from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def deck_keyboard() -> InlineKeyboardMarkup:
    keyboard_buttons = [
        [InlineKeyboardButton(text="Нильфгард", callback_data="deck:nil")],
        [InlineKeyboardButton(text="Чудовища", callback_data="deck:ch")],
        [InlineKeyboardButton(text="Королевство Севера", callback_data="deck:ks")],
        [InlineKeyboardButton(text="Скоя’таэли", callback_data="deck:s")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

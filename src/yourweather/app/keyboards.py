from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

welcome = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Указать город", callback_data="send_city_")],
        [InlineKeyboardButton(text="⏱️ Указать время", callback_data="send_time_")],
    ],
    resize_keyboard=True,
)

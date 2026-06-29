from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

welcome = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Указать город", callback_data="send_city_")],
        [InlineKeyboardButton(text="⏱️ Указать время", callback_data="send_time_")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="check_profile_")],
    ],
    resize_keyboard=True,
)

back = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="👈 Назад", callback_data="back_")],
    ],
    resize_keyboard=True,
)

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

seria_keyboard = InlineKeyboardMarkup(row_width=3)
seria_keyboard.add(
    InlineKeyboardButton("AA", callback_data="AA"),
    InlineKeyboardButton("AB", callback_data="AB"),
    InlineKeyboardButton("AC", callback_data="AC"),
    InlineKeyboardButton("AD", callback_data="AD"),
    InlineKeyboardButton("AE", callback_data="AE"),
    InlineKeyboardButton("KA", callback_data="KA"),
)

number_keyboard = InlineKeyboardMarkup(row_width=3)
number_keyboard.add(
    InlineKeyboardButton("1️⃣", callback_data="1"),
    InlineKeyboardButton("2️⃣", callback_data="2"),
    InlineKeyboardButton("3️⃣", callback_data="3"),
    InlineKeyboardButton("4️⃣", callback_data="4"),
    InlineKeyboardButton("5️⃣", callback_data="5"),
    InlineKeyboardButton("6️⃣", callback_data="6"),
    InlineKeyboardButton("7️⃣", callback_data="7"),
    InlineKeyboardButton("8️⃣", callback_data="8"),
    InlineKeyboardButton("9️⃣", callback_data="9"),
    InlineKeyboardButton("◀️", callback_data="number_back"),
    InlineKeyboardButton("0️⃣", callback_data="0"),
)

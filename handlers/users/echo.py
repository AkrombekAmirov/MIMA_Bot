from keyboards.inline.keyboards_inline import choose_visitor
from aiogram import types
from loader import dp


# Echo bot
@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    await message.answer(
        f"Xurmatli {message.from_user.full_name} siz ruxsat etilmagan ma'lumot kiritdingiz. \n ❌<b>{message.text}</b>❌\nQuyidagi xizmatlar mavjud",
        reply_markup=choose_visitor)

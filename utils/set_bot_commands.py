from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Botni boshiga qaytarish uchun /start ni bosing."),
            # types.BotCommand("help", "Yordam"),
        ]
    )

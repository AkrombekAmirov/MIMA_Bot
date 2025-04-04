# from aiogram.dispatcher.middlewares import BaseMiddleware
# from aiogram.dispatcher.handler import CancelHandler
# from aiogram import types
# from loader import bot
# from utils import check
# from data import CHANEL
#
#
# class CheckSub(BaseMiddleware):
#     async def on_process_message(self, update: types.Message, data: dict):
#         print(update.message_id, update.chat.id, update)
#         if update.chat:
#             user = update.from_user.id
#         elif update.from_user:
#             user = update.from_user.id
#         result = "Botdan foydalanish uchun quyidagi guruhga obuna bo'ling:\n"
#         final_status = True
#         status = await check(user_id=user, chanel=CHANEL)
#         final_status = status
#         chanel_info = await bot.get_chat(CHANEL)
#         if not status:
#             # Guruh uchun taklif havolasi
#             invite_link = await bot.export_chat_invite_link(CHANEL)
#             result = (f"📢 <b>Diqqat!</b>\n"
#             f"Botdan foydalanish uchun quyidagi guruhga obuna bo'lishingiz kerak:\n\n"
#             f"👉 <a href='{invite_link}'><b>👥 {chanel_info.title}</b> — Obuna bo‘lish</a>\n"
#             f"✅ Obuna bo'lgandan keyin /start tugmasini bosing!")
#
#         if not final_status:
#             await update.answer(result, disable_web_page_preview=True)
#             raise CancelHandler()
#

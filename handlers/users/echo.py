from keyboards.inline.keyboards_inline import choose_visitor
from aiogram.types import ContentType
from aiogram import types
from loader import dp


@dp.message_handler(state=None, content_types=ContentType.ANY)
async def handle_unexpected_content(message: types.Message):
    content_type = message.content_type
    user_name = message.from_user.full_name
    readable_type = {
        ContentType.TEXT: f"❌<b>{message.text}</b>❌",
        ContentType.PHOTO: "📷 rasm",
        ContentType.DOCUMENT: "📄 hujjat",
        ContentType.VIDEO: "🎥 video",
        ContentType.AUDIO: "🎵 audio",
        ContentType.VOICE: "🎙 ovozli xabar",
        ContentType.STICKER: "🔖 sticker",
        ContentType.CONTACT: "👤 kontakt",
        ContentType.LOCATION: "📍 joylashuv",
        ContentType.ANIMATION: "📹 gif"
    }.get(content_type, "❓ noma’lum turdagi fayl")

    await message.answer(
        f"Xurmatli {user_name}, siz ruxsat etilmagan ma'lumot yubordingiz: {readable_type}.\n"
        "Iltimos, suralgan ma'lumotni yuboring!",
        reply_markup=choose_visitor
    )

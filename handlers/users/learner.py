from file_service import write_qabul, get_file_path, check_passport_exists
from keyboards.inline.Dictionary import faculty_file_map2
from utils.db_api.core import DatabaseService1, User
from data.config import ADMIN_M2, DATABASE_URL
from aiogram.dispatcher import FSMContext
from LoggingService import LoggerService
from states.button import Learning
from datetime import datetime
from functools import wraps
from asyncio import sleep
from aiogram import types
from loader import dp
from re import match
import logging
import re
from keyboards.inline import (
    keyboard, yonalish_nomi_keyboard, response_keyboard,
    uzbekistan_viloyatlar, choose_visitor,
    seria_keyboard, number_keyboard, list_regioin,
    list_tuman, list_region1, inline_tumanlar,
    choose_education_status, choose_language
)

# Fayl junatishni bloklash uchun handler
dp.message_handler(content_types=[types.ContentType.DOCUMENT,
                                  types.ContentType.PHOTO,
                                  types.ContentType.VIDEO,
                                  types.ContentType.AUDIO,
                                  types.ContentType.VOICE,
                                  types.ContentType.VIDEO_NOTE])


async def block_file_upload(message: types.Message):
    await message.answer(
        "❌ Fayl yuborish imkoniyati o'chirilgan.\nBotga fayl yuborish mumkin emas.\nIltimos, /start buyruqini yuboring.")
    return False  # Handler chain'ni to'xtatish uchun


# Logging config
logging.basicConfig(
    filename='bot.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# logger = LoggerService().get_logger()
db = DatabaseService1(logger=LoggerService())


def handle_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logging.exception(f"Xatolik: {func.__name__}: {e}")
            if isinstance(args[0], types.CallbackQuery):
                await args[0].answer("❌ Xatolik yuz berdi. Qaytadan urinib ko‘ring.")
            elif isinstance(args[0], types.Message):
                await args[0].answer("❌ Noto‘g‘ri amal. Qaytadan urinib ko‘ring.")
            return None

    return wrapper


class BotHandler:
    @staticmethod
    @dp.message_handler(commands=["start"])
    @handle_errors
    async def start(message: types.Message, state: FSMContext):
        await state.reset_state(with_data=True)
        await message.answer("Xizmat turini tanlang:", reply_markup=choose_visitor)

    @staticmethod
    @dp.message_handler(content_types=[types.ContentType.CONTACT, types.ContentType.TEXT])
    @handle_errors
    async def process_contact(message: types.Message, state: FSMContext):
        if message.content_type != types.ContentType.CONTACT:
            await message.answer("❗ Iltimos, tugma orqali kontakt yuboring.")
            return
        user_id = str(message.from_user.id)
        contact = message.contact
        if await db.get(User, filters={'telegram_id': user_id}):
            await message.answer("✅ Siz ro'yxatdan o'tgansiz. Xizmat turini tanlang:", reply_markup=choose_visitor)
        elif contact.user_id == message.from_user.id:
            await db.add(User(
                telegram_id=user_id,
                username=message.from_user.username or "",
                telegram_name=message.from_user.full_name,
                telegram_number=contact.phone_number,
                status=False,
                test_point='1'
            )
            )  # Sevimli , Mening yurtim,
            await state.update_data({"telegram_number": contact.phone_number})
            await message.answer("Xizmat turini tanlang:", reply_markup=choose_visitor)
        else:
            await message.answer("❌ Bu kontakt sizga tegishli emas. Iltimos, o‘z kontaktingizni yuboring.")

    @staticmethod
    @dp.callback_query_handler(text="registration")
    @handle_errors
    async def registration(call: types.CallbackQuery, state: FSMContext):
        if not await db.get(User, filters={"telegram_id": str(call.from_user.id)}):
            await call.message.answer("📲 Iltimos, telegram kontaktangizni yuboring.", reply_markup=keyboard)
        else:
            await call.message.answer(
                "❗ <b>Eslatma:</b>\n"
                "Ro‘yxatdan o‘tish jarayonida sizdan bir necha bosqichda ma’lumot so‘raladi. "
                "Agar biror bosqichda xatolik yuz bersa — xavotir olmang.\n\n"
                "📌 So‘nggi bosqichda siz kiritgan barcha ma’lumotlarni ko‘rib chiqish va tasdiqlash imkoniyatingiz bo‘ladi. "
                "Agar xato bo‘lsa, <b>“⬅️ Orqaga”</b> tugmasi orqali to‘g‘rilashingiz mumkin.\n\n"
                "Iltimos, ma’lumotlarni diqqat bilan va <b>lotin harflarida</b> kiriting.",
                parse_mode="HTML"
            )

            # 5 soniyalik sanash effekti
            for i in range(10, 0, -1):
                await sleep(1)
                await call.message.edit_text(
                    f"❗ Quyidagi ogohlantirishni o'qib chiqing...\n\n"
                    f"⏳ Keyingi bosqich <b>{i}</b> soniyadan so‘ng boshlanadi.",
                    parse_mode="HTML"
                )

            await call.message.edit_text("✅ Rahmat! Endi davom etamiz.", parse_mode="HTML")

            await call.message.answer("📚 O‘quv yo‘nalishini tanlang:", reply_markup=yonalish_nomi_keyboard)

    @staticmethod
    @dp.callback_query_handler(lambda call: call.data.startswith("faculty"))
    @handle_errors
    async def faculty(call: types.CallbackQuery, state: FSMContext):
        await state.update_data({"yonalish": call.data})
        await call.message.delete()
        await call.message.answer("🎓 Ta'lim shaklini tanlang:", reply_markup=choose_education_status)

    @staticmethod
    @dp.callback_query_handler(lambda call: call.data in ["Kunduzgi", "Sirtqi"])
    @handle_errors
    async def education_status(call: types.CallbackQuery, state: FSMContext):
        await state.update_data({"education_status": call.data})
        await call.message.delete()
        await call.message.answer("🌐 Ta'lim tilini tanlang:", reply_markup=choose_language)

    @staticmethod
    @dp.callback_query_handler(lambda call: call.data in ["O'zbek tili", "Rus tili"])
    @handle_errors
    async def language(call: types.CallbackQuery, state: FSMContext):
        await state.update_data({"leanguage": call.data})
        await call.message.delete()
        await call.message.answer("📍 Viloyatingizni tanlang:", reply_markup=uzbekistan_viloyatlar)

    @staticmethod
    @dp.callback_query_handler(lambda call: call.data in list_regioin)
    @handle_errors
    async def region(call: types.CallbackQuery, state: FSMContext):
        region_index = int(call.data[3:])
        await state.update_data({"region": list_region1[region_index]})
        await call.message.delete()
        await call.message.answer("🏙 Tumanni tanlang:", reply_markup=await inline_tumanlar(call.data))

    @staticmethod
    @dp.callback_query_handler(lambda call: call.data in list_tuman)
    @handle_errors
    async def phone_numbers(call: types.CallbackQuery, state: FSMContext):
        await state.update_data({"tuman": call.data})
        await call.message.delete()
        await call.message.answer(
            "📞 Iltimos, Siz bilan bog'lanish uchun qo‘shimcha telefon raqamingizni matn shaklida kiriting:")
        await Learning.minus.set()

    @staticmethod
    @dp.message_handler(content_types=types.ContentType.TEXT, state=Learning.minus)
    @handle_errors
    async def district(message: types.Message, state: FSMContext):
        if not re.match(r'^\+998\d{9}$', message.text.strip()):
            await message.answer(
                "❌ Telefon raqami noto‘g‘ri formatda.\nIltimos, quyidagi shaklda kiriting:\n\n`+998901234567`",
                parse_mode="Markdown")
            await Learning.minus.set()
            return
        if message.text.strip() == "+998901234567":
            await message.answer(
                f"❌ O'zingizga tegishli bo'lmagan telefon raqam kiritdingiz! Iltimos ozingizga tegishli telefon raqamni kiriting.", )
            await Learning.minus.set()
            return
        await state.update_data({"phone_numbers": message.text})
        await message.delete()
        await message.answer("👤 Familiya, ism va sharifingizni kiriting:")
        await Learning.next()

    @staticmethod
    @dp.message_handler(content_types=types.ContentType.TEXT, state=Learning.zero)
    @handle_errors
    async def process_name(message: types.Message, state: FSMContext):
        full_name = message.text.strip()
        # Faqat lotin harflari, bo'sh joy, apostrof va tire
        if not match(r"^[A-Za-z\s'-]+$", full_name):
            await message.answer("❌ Iltimos, faqat *lotin harflarida* familiya, ism va sharifingizni kiriting.")
            await Learning.zero.set()
            return
        # Kamida ism va familiya (2 ta so'z) bo'lishi kerak
        parts = full_name.split()
        if len(parts) < 2:
            await message.answer("❌ Iltimos, to‘liq familiya va ismingizni kiriting (kamida 2 ta so‘z).")
            await Learning.zero.set()
            return
        await state.update_data({"Name": message.text})
        await message.delete()
        await message.answer("🆔 JSHIR (14 xonali raqam) kiriting:")
        await Learning.next()

    @staticmethod
    @dp.message_handler(content_types=types.ContentType.TEXT, state=Learning.one)
    @handle_errors
    async def process_jshir(message: types.Message, state: FSMContext):
        if not (message.text.isdigit() and len(message.text) == 14):
            await message.answer("❌ JSHIR noto'g‘ri. U 14 xonali raqam bo‘lishi kerak.")
            return await Learning.one.set()

        await state.update_data({"jshir": message.text})
        await message.answer("🛂 Passport seriyasini tanlang:", reply_markup=seria_keyboard)
        await Learning.next()

    @staticmethod
    @dp.callback_query_handler(lambda call: call.data in ["AA", "AB", "AC", "AD", "AE", "KA"], state=Learning.two)
    @handle_errors
    async def process_passport_seria(call: types.CallbackQuery, state: FSMContext):
        await state.update_data({"passport_seria": call.data})
        await call.message.delete()
        await call.message.answer("🔢 Passport raqamini kiriting:", reply_markup=number_keyboard)
        await Learning.next()

    @staticmethod
    @dp.callback_query_handler(lambda call: call.data in list("0123456789") + ["number_back"], state=Learning.three)
    @handle_errors
    async def process_passport_number(call: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        current = data.get("passport_number", "")
        updated = current[:-1] if call.data == "number_back" else current + call.data
        await state.update_data({"passport_number": updated})

        if len(updated) == 7:
            passport = f"{data.get('passport_seria')}{updated}"
            if await db.get(User, filters={"passport": passport}):
                await call.message.answer("❗ Bu passport bilan ro'yxatdan o'tilgan.", reply_markup=choose_visitor)
                return await state.reset_state(with_data=True)
            if await check_passport_exists(str(passport)):
                await call.message.answer("❗ Akademiya talabalari uchun ro'yhatdan o'tish imkoniyati mavjud emas!",
                                          reply_markup=choose_visitor)
                return await state.reset_state(with_data=True)

            await state.update_data({"passport": passport})
            info = (
                f"Quyidagi ma'lumotlar to'g‘rimi?\n\n"
                f"👤 F I SH: <b>{data.get('Name')}</b>\n"
                f"📞 Telefon raqami: <b>{data.get('phone_numbers')}</b>\n"
                f"🆔 JSHIR: <b>{data.get('jshir')}</b>\n"
                f"🛂 Passport: <b>{passport}</b>\n"
                f"📍 Manzil: <b>{data.get('region')}</b>, {data.get('tuman')}\n"
                f"📚 Yo'nalish: <b>{faculty_file_map2.get(data.get('yonalish'))}</b>\n"
                f"🎓 Shakli: <b>{data.get('education_status')}</b>\n"
                f"🌐 Tili: <b>{data.get('leanguage')}</b>"
            )
            await call.message.answer(info, reply_markup=response_keyboard, parse_mode="HTML")
            await Learning.four.set()
        else:
            await call.message.edit_text(f"🔢 Raqam kiriting: {data.get('passport_seria')} {updated}",
                                         reply_markup=number_keyboard)

    @staticmethod
    @dp.callback_query_handler(lambda call: call.data in ["yes", "no"], state=Learning.four)
    @handle_errors
    async def confirm_data(call: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        print((await db.get(User, filters={'telegram_id': str(call.from_user.id)}))[0].telegram_number)
        if call.data == "yes":
            # user: User = await db.get(User, filters={'telegram_id': str(call.from_user.id)})
            updates = {
                "name": data.get("Name"),
                "passport": data.get("passport"),
                "viloyat": data.get("region"),
                "tuman": data.get("tuman"),
                "faculty": faculty_file_map2.get(data.get("yonalish")),
                "talim_turi": data.get("education_status"),
                "talim_tili": data.get("leanguage"),
                "jshir_id": data.get("jshir"),
                "phone_number": data.get("phone_numbers"),
                "created_date": datetime.now().strftime("%Y-%m-%d"),
                "created_time": datetime.now().strftime("%H:%M:%S")
            }
            await db.update_user_by_telegram_id(telegram_id=str(call.from_user.id), updates=updates)
            await write_qabul([
                data.get("Name"),
                faculty_file_map2.get(data.get("yonalish")),
                data.get("leanguage"),
                data.get("education_status"),
                data.get("passport"),
                data.get("jshir"),
                data.get("region"),
                data.get("tuman"),
                (await db.get(User, filters={'telegram_id': str(call.from_user.id)}))[0].telegram_number,
                data.get("phone_numbers"),
                datetime.now().strftime("%Y-%m-%d")
            ])
            await state.reset_state(with_data=True)
            await dp.bot.send_message(ADMIN_M2,
                                      f"👤 F.I.SH: <b>{data.get('Name')}</b>\n"
                                      f"📞 Telefon raqami: <b>{data.get('phone_numbers')}</b>\n"
                                      f"🆔 JSHIR: <b>{data.get('jshir')}</b>\n"
                                      f"🛂 Passport: <b>{data.get('passport')}</b>\n"
                                      f"📍 Manzil: <b>{data.get('region')}</b>, {data.get('tuman')}\n"
                                      f"📚 Yo'nalish: <b>{faculty_file_map2.get(data.get('yonalish'))}</b>\n"
                                      f"🎓 Shakli: <b>{data.get('education_status')}</b>\n"
                                      f"🌐 Tili: <b>{data.get('leanguage')}</b>")
            await dp.bot.send_document(ADMIN_M2, types.InputFile(await get_file_path(name="qabul.xlsx")))
            await call.message.answer("✅ Ma’lumotlar saqlandi! \n", reply_markup=choose_visitor)
        else:
            await state.reset_state(with_data=True)
            await call.message.answer("❌ Ma'lumotlar bekor qilindi.\nQaytadan urinib ko'ring",
                                      reply_markup=choose_visitor)

from keyboards.inline import choose_education_status_info, choose_visitor
from aiogram.dispatcher import FSMContext
from file_service import get_file_path
from aiogram import types
from loader import dp
import os


@dp.callback_query_handler(text="information")
async def information(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(" <b>📘 Ta’lim shakllari va litsenziya haqida</b>\n\n",
                              reply_markup=choose_education_status_info)


@dp.callback_query_handler(lambda call: call.data in ["Kunduzgi_info", "Sirtqi_info", "license_info"])
async def education_status_info(call: types.CallbackQuery, state: FSMContext):
    if call.data == "Kunduzgi_info":
        data = (
            "📚 <b>Kunduzgi ta'lim yo'nalishlari bo'yicha to'lov-shartnoma miqdorlari:</b>\n\n"
            "1. 🛠 <b>Mehnat muhofazasi va texnika xavfsizligi</b> — <b>17 mln so'm</b>\n"
            "2. 🧯 <b>Hayot faoliyati xavfsizligi</b> — <b>14 mln so'm</b>\n"
            "3. 👥 <b>Inson resurslarini boshqarish</b> — <b>17 mln so'm</b>\n"
            "4. 🤝 <b>Ijtimoiy ish</b> — <b>14 mln so'm</b>\n"
            "5. 🧠 <b>Psixologiya</b> — <b>17 mln so'm</b>\n"
            "6. 📈 <b>Menejment</b> — <b>20 mln so'm</b>\n"
            "7. ⚖️ <b>Yurisprudensiya</b> — <b>30 mln so'm</b>\n"
            "8. 📊 <b>Bugalteriya hisobi</b> — <b>20 mln so'm</b>\n"
            "9. 🧪 <b>Metrologiya va standartlashtirish</b> — <b>17 mln so'm</b>\n\n"
            "⏰ <b>O'qish davomiyligi:</b> 4️⃣ yil\n"
            "📌 <b>Izoh:</b> Barcha narxlar yillik to'lov miqdorini o'z ichiga oladi."
        )
        await call.message.answer(text=data, parse_mode="HTML")
    elif call.data == "Sirtqi_info":
        data = (
            "📚 <b>Sirtqi ta'lim yo'nalishlari bo'yicha to'lov-shartnoma miqdorlari:</b>\n\n"
            "1. 🛠 <b>Mehnat muhofazasi va texnika xavfsizligi</b> — <b>15 mln so'm</b>\n"
            "2. 🧯 <b>Hayot faoliyati xavfsizligi</b> — <b>13 mln so'm</b>\n"
            "3. 👥 <b>Inson resurslarini boshqarish</b> — <b>15 mln so'm</b>\n"
            "4. 🤝 <b>Ijtimoiy ish</b> — <b>13 mln so'm</b>\n"
            "5. 🧠 <b>Psixologiya</b> — <b>15 mln so'm</b>\n"
            "6. 📈 <b>Menejment</b> — <b>18 mln so'm</b>\n"
            "7. ⚖️ <b>Yurisprudensiya</b> — <b>27 mln so'm</b>\n"
            "8. 📊 <b>Bugalteriya hisobi</b> — <b>18 mln so'm</b>\n"
            "9. 🧪 <b>Metrologiya va standartlashtirish</b> — <b>15 mln so'm</b>\n\n"
            "⏰ <b>O'qish davomiyligi:</b> 5️⃣ yil\n"
            "📌 <b>Izoh:</b> Barcha narxlar yillik to'lov miqdorini o'z ichiga oladi."
        )
        await call.message.answer(text=data, parse_mode="HTML")
    elif call.data == "license_info":
        license_path = await get_file_path("license.pdf")
        print(license_path)
        if os.path.exists(license_path):
            caption = "<b>📄 Rasmiy Litsenziya</b>\n\n"
            await call.message.answer_document(
                types.InputFile(license_path),
                caption=caption,
                parse_mode="HTML"
            )

    await call.message.answer(text="Xizmat turini tanlang", reply_markup=choose_visitor)

from file_service import get_report_file_path, create_report_file
from utils.db_api.core import DatabaseService1, User
from aiogram.dispatcher import FSMContext
from datetime import datetime, time
from collections import Counter
from aiogram import types
from loader import dp, bot
import os, asyncio, logging

db = DatabaseService1()

@dp.message_handler(commands=["hisobot"])
async def hisobot_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
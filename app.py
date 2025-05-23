#!/usr/bin/env python3
import os
import sys
import signal
import asyncio
import logging
import tracemalloc
import psutil
from time import time
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.utils.executor import start_polling
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# --- Import qilish orqali barcha handler/filter/middleware’lar ro‘yxatga olinadi
import middlewares  # noqa: F401
import filters      # noqa: F401
import handlers     # noqa: F401

from utils.set_bot_commands import set_default_commands
from utils.notify_admins import on_startup_notify

# --- ENV sozlamalari
API_TOKEN = os.getenv("BOT_TOKEN")
METRICS_PORT = int(os.getenv("METRICS_PORT", "8001"))

if not API_TOKEN:
    print("❌ BOT_TOKEN muhit o‘zgaruvchisi topilmadi!", file=sys.stderr)
    sys.exit(1)

# --- LOGGING SOZLAMALARI
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")

# 1) Console handler
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(formatter)
logger.addHandler(ch)

# 2) Rotating file handler (10MB, 5 backup)
fh = RotatingFileHandler("bot.log", maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")
fh.setFormatter(formatter)
logger.addHandler(fh)

# --- METRICS (Prometheus eksporteri)
from prometheus_client import start_http_server, Gauge

tracemalloc.start()
start_http_server(METRICS_PORT)

MEM_USED = Gauge("bot_memory_bytes", "Bot Xotira ishlatishi (bytes)")
CPU_PERCENT = Gauge("bot_cpu_percent", "Bot CPU foizi")
UPTIME = Gauge("bot_uptime_seconds", "Bot ishlagan vaqti (sekundda)")
START_TIME = time()

async def monitor_metrics():
    """Har 15 soniyada metrics yangilash."""
    proc = psutil.Process(os.getpid())
    while True:
        MEM_USED.set(tracemalloc.get_traced_memory()[1])
        CPU_PERCENT.set(proc.cpu_percent(interval=None))
        UPTIME.set(time() - START_TIME)
        await asyncio.sleep(15)

# --- GLOBAL EXCEPTION HANDLER
def handle_loop_exception(loop, context):
    msg = context.get("exception", context["message"])
    logger.error(f"Ciklizanmagan xato tutildi: {msg}", exc_info=True)

# --- BOT & DISPATCHER
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ——————————————
# STARTUP & SHUTDOWN
# ——————————————
async def on_startup(dispatcher: Dispatcher):
    logger.info("🔄 Bot startup boshlab†")
    try:
        await set_default_commands(dispatcher)
        logger.info("✅ Default komandalar o‘rnatildi")
        await on_startup_notify(dispatcher)
        logger.info("✅ Adminlarga startup xabari yuborildi")
    except Exception:
        logger.exception("❌ on_startup jarayonida xato")

async def on_shutdown(dispatcher: Dispatcher):
    logger.info("🔔 Bot shutdown boshlab†")
    try:
        # await on_shutdown_notify(dispatcher)
        logger.info("✅ Adminlarga shutdown xabari yuborildi")
    except Exception:
        logger.exception("❌ on_shutdown_notify jarayonida xato")
    finally:
        # FSM storage ni toza yopish
        try:
            await dispatcher.storage.close()
            await dispatcher.storage.wait_closed()
            logger.info("✅ Dispatcher storage yopildi")
        except Exception:
            logger.exception("❌ Storage yopishda xato")

# ——————————————
# SIGNAL HANDLER
# ——————————————
def _signal_handler(signum, frame):
    logger.warning(f"⚠️ SIgnal {signum} olindi, shutdown chaqirilmoqda…")
    # Hech narsa – start_polling o‘z shutdown hook’ini chaqiradi

signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)

# ——————————————
# ASOSIY FUNKSIYA
# ——————————————
def main():
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_loop_exception)
    # Metrics monitor parallel task
    loop.create_task(monitor_metrics())
    # Boshlaymiz pollingni
    start_polling(
        dp,
        skip_updates=True,       # backlog’dagi eski update’larni o‘tkazib yuborish
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        loop=loop
    )

if __name__ == "__main__":
    main()

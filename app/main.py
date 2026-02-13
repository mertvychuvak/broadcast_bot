import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from database import init_db
from handlers import router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(router)


async def main():
    await init_db()
    print("🚀 Bot started (polling mode)")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

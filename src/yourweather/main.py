from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from YourWeather.src.yourweather.config import settings
from YourWeather.src.yourweather.app.handlers import router
from YourWeather.src.yourweather.app.database.requests import initializator_database

import asyncio
import logging

bot = Bot(token=..., default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

async def run():
    await initializator_database()

    dp.include_router(router)
    await dp.start_polling()


if __name__ == "__main__":
    logging = logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("EXIT")
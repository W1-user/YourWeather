from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from yourweather.config import settings
from yourweather.app.handlers import router, setup_scheduler
from yourweather.app.database.models import initializator_database
from yourweather.app.scheduler import WeatherScheduler

import asyncio
import logging

bot = Bot(
    token=settings.bot.token,
    default=DefaultBotProperties(parse_mode=settings.bot.parse_mode),
)
dp = Dispatcher()


async def run():
    scheduler = None
    try:
        await initializator_database()

        scheduler = WeatherScheduler(bot)
        setup_scheduler(scheduler)

        await scheduler.start()

        dp.include_router(router)
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("EXIT!!!")
    finally:
        if scheduler:
            await scheduler.stop()
        await bot.session.close()

if __name__ == "__main__":
    logging = logging.basicConfig(level=logging.INFO)
    asyncio.run(run())
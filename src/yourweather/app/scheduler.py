from aiogram import Bot
from sqlalchemy import select

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from yourweather.app.database.models import User, async_session
from yourweather.app.weather_service import weather_sender

class WeatherScheduler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
        self.job_ids = set()

    async def start(self):
        self.scheduler.start()
        await self.load_all_user_jobs()

    async def load_all_user_jobs(self):
        async with async_session() as session:
            stmt = select(User).where(
                User.city.isnot(None),
                User.tts.isnot(None),
            )
            result = await session.execute(stmt)
            users = result.scalars().all()

            for user in users:
                await self.add_jobs_for_users(user.tg_id, user.city, user.tts)


    async def add_jobs_for_users(self, user_id: int, city: str, tts: str):
        try:

            hour, minute = map(int, tts.split(":"))
            job_id = f"weather_{user_id}"

            job = self.scheduler.add_job(
                func=self.send_weather_to_user,
                trigger=CronTrigger(hour=hour, minute=minute),
                args=[user_id],
                id=job_id,
                replace_existing=True,
                misfire_grace_time=60,
            )
            self.job_ids.add(job_id)
            return True
        
        except Exception as e:
            print(f"Произошла ошибка - {e}")
            return False

    async def send_weather_to_user(self, user_id: int):
        try:
            async with async_session() as session:
                stmt = select(User).where(User.tg_id == user_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()

                if not user or not user.city or not user.tts:
                    print(f"У Юзера - {user.tg_id}: не обнаружен город или время")
                    return
                
                await weather_sender(self.bot, user.city, user_id)
            
        except Exception as e:
            print(f"Произошла ошибка - {e}")
    
    async def refresh_user_job(self, user_id: int):
        async with async_session() as session:
            stmt = select(User).where(User.tg_id == user_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            if not user:
                print(f"Юзер - {user_id}: не найден")
                return False
            
            if user.city and user.tts:
                return await self.add_jobs_for_users(user_id, user.city, user.tts)
            
            else:
                job_id = f"weather_{user_id}"
                if job_id in self.job_ids:
                    try:
                        self.scheduler.remove_job(job_id)
                        self.job_ids.remove(job_id)
                        print("Задача была удалена")

                    except Exception as e:
                        print(f"Произошла ошибка - {e}")

                return False
            
    async def stop(self):
        self.scheduler.shutdown()
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from sqlalchemy import select, update
from yourweather.app.database.models import User, async_session
from yourweather.app.scheduler import WeatherScheduler

import yourweather.app.keyboards as kb

router = Router()


class Form(StatesGroup):
    city = State()
    time = State()

    last_message_id = State()


def setup_scheduler(sched: WeatherScheduler):
    global scheduler
    scheduler = sched

@router.message(CommandStart())
async def welcome(msg: Message):
    async with async_session() as session:
        stmt = select(User).where(User.tg_id == msg.from_user.id)
        result = await session.execute(stmt)
        user = result.one_or_none()

        username = msg.from_user.username
        if not user:
            new_user = User(
                tg_id=msg.from_user.id,
                username=username if username else "None",
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

    await msg.reply(
        f"<b>Привет, {msg.from_user.first_name}!\nЧто будем указывать, для отправки погоды ежедневно?</b>",
        reply_markup=kb.welcome,
    )


@router.callback_query(F.data == "send_city_")
async def send_city(cq: CallbackQuery, state: FSMContext): 
    await state.set_state(Form.city)
    await cq.message.delete()

    message = await cq.message.answer(f"<b>Введите нужный вам город (На латинице):</b>")
    
    await state.update_data(last_message_id=message.message_id)
    await cq.answer()

@router.message(Form.city)
async def send_data_city_database(msg: Message, state: FSMContext):
    await state.update_data(city=msg.text)
    data = await state.get_data()

    if "last_message_id" in data:
        try:
            await msg.bot.delete_message(
                chat_id=msg.chat.id,
                message_id=data["last_message_id"],
            )
        except:
            pass
    
    await msg.delete()

    async with async_session() as session:
        stmt = select(User).where(User.tg_id == msg.from_user.id)
        result = await session.execute(stmt)
        user = result.one_or_none()

        username = msg.from_user.username
        if not user:
            new_user = User(
                tg_id=msg.from_user.id,
                username=username if username else "None",
                city=data["city"],
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

        upd_user = (
            update(User)
            .where(User.tg_id == msg.from_user.id)
            .values(
                city=data["city"],
            )
        )

        await session.execute(upd_user)
        await session.commit()

    if scheduler:
        await scheduler.refresh_user_job(msg.from_user.id)

    await msg.answer(
        f"<b>Привет еще раз, {msg.from_user.first_name}!\nЧто будем указывать, для отправки погоды ежедневно?</b>",
        reply_markup=kb.welcome,
    )


@router.callback_query(F.data == "send_time_")
async def send_tts(cq: CallbackQuery, state: FSMContext):
    await state.set_state(Form.time)
    await cq.message.delete()

    message = await cq.message.answer(
        f"<b>Пример: 12:00 или 12:35\nВведите нужное время отправки:</b>"
    )
    await state.update_data(last_message_id=message.message_id)


@router.message(Form.time)
async def send_data_time_database(msg: Message, state: FSMContext):
    await state.update_data(time=msg.text)
    data = await state.get_data()

    if "last_message_id" in data:
        try:
            await msg.bot.delete_message(
                chat_id=msg.chat.id,
                message_id=data["last_message_id"],
            )
        except:
            pass

    await msg.delete()
    
    try:
        hour, minute = map(int, data["time"].split(":"))
        if not 0 <= hour <= 59 or not 0 <= minute <= 59:
                raise ValueError("Не верно введены значения")
    except:
        await msg.answer("Неверный формат. Используйте ЧЧ:ММ (например, 12:00)")
        return

    async with async_session() as session:
        stmt = select(User).where(User.tg_id == msg.from_user.id)
        result = await session.execute(stmt)
        user = result.one_or_none()

        username = msg.from_user.username
        if not user:
            new_user = User(
                tg_id=msg.from_user.id,
                username=username if username else "None",
                tts=data["time"],
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)

        upd_user = (
            update(User)
            .where(User.tg_id == msg.from_user.id)
            .values(
                tts=data["time"],
            )
        )

        await session.execute(upd_user)
        await session.commit()

    if scheduler:
        await scheduler.refresh_user_job(msg.from_user.id)

    await msg.answer(
        f"<b>Привет еще раз, {msg.from_user.first_name}!\nЧто будем указывать, для отправки погоды ежедневно?</b>",
        reply_markup=kb.welcome,
    )

@router.callback_query(F.data == "check_profile_")
async def check_profile(cq: CallbackQuery):
    async with async_session() as session:
        stmt = select(User).where(User.tg_id == cq.from_user.id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

    city = user.city
    time = user.tts
    notification = "Активно" if city and time else "Неактивно"

    await cq.message.edit_text(
        "<b>Твой профиль:</b>\n\n"
        f"<b>Город: {city}</b>\n"
        f"<b>Время оповещения: {time}\n</b>"
        f"<b>Оповощение: {notification}</b>",
        reply_markup=kb.back
    )

@router.callback_query(F.data == "back_")
async def menu(cq: CallbackQuery):
    await cq.message.edit_text(
        f"<b>Привет еще раз, {cq.from_user.first_name}!\nЧто будем указывать, для отправки погоды ежедневно?</b>",
        reply_markup=kb.welcome,
    )
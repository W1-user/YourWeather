from aiogram import Bot
from yourweather.config import settings

import requests as r


async def get_weather(city: str):
    link = "http://api.weatherapi.com/v1"
    params = {"key": settings.weather.token, "q": city, "lang": "ru", "aqi": "no"}

    try:
        response = r.get(f"{link}/current.json", params=params)
        response.raise_for_status()

        return response.json()

    except Exception as e:
        print(f"Произошла ошибка при получени погоды - {e}")
        return False


async def formulating_weather(city: str):
    data = await get_weather(city)

    if not data:
        print("Не удалось получить данные...")
        return

    location = data["location"]
    current = data["current"]

    text = (
        f"<b>ПОГОДА В ГОРОДЕ: {location["name"].upper()}</b>\n"
        "<b>-----------------</b>\n"
        f"<b>Регион: {location["region"]}, {location["country"]}</b>\n"
        f"<b>Местное время: {location["localtime"]}</b>\n"
        "<b>-----------------</b>\n"
        f"<b>Температура: {current["temp_c"]}°C</b>\n"
        f"<b>Ощущается как: {current['feelslike_c']}°C</b>\n"
        f"<b>Погода: {current["condition"]["text"]}</b>\n"
        f"<b>Влажность: {current["humidity"]}</b>\n"
        f"<b>Ветер: {current["wind_kph"]} км/ч</b>\n"
        f"<b>Порыв ветра: {current["gust_kph"]} км/ч</b>\n"
        f"<b>Осадки: {current["precip_mm"]} мм</b>\n"
        "<b>-----------------</b>\n"
        f"<b>Обновлено: {current["last_updated"]}</b>\n"
    )

    return text


async def weather_sender(bot: Bot, city: str, user_id: int):

    text = await formulating_weather(city)

    await bot.send_message(
        chat_id=int(user_id),
        text=text,
    )

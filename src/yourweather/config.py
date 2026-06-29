import os

from pydantic import BaseModel
from pydantic_settings import BaseSettings

from dotenv import load_dotenv

load_dotenv()


class DatabaseSettings(BaseModel):
    url: str = os.getenv("DATABASE_URL")
    echo: bool = False
    eoc: bool = False


class BotSettings(BaseModel):
    token: str = os.getenv("BOT_TOKEN")
    parse_mode: str = os.getenv("PARSE_MODE")


class WeatherSettings(BaseModel):
    token: str = os.getenv("WEATHER_TOKEN")


class Settings(BaseSettings):
    database: DatabaseSettings = DatabaseSettings()
    bot: BotSettings = BotSettings()
    weather: WeatherSettings = WeatherSettings()


settings = Settings()

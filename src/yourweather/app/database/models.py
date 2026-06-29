from sqlalchemy import String, Integer, BigInteger, Float
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs

from yourweather.config import settings

engine = create_async_engine(url=settings.database.url, echo=settings.database.echo)
async_session = async_sessionmaker(engine, expire_on_commit=settings.database.eoc)


class Base(DeclarativeBase, AsyncAttrs):
    pass


class User(Base):
    __tablename__ = "users"

    # Profile
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    tg_id: Mapped[int] = mapped_column(BigInteger, index=True)
    username: Mapped[str] = mapped_column(String, default="None", index=True)

    # Config
    city: Mapped[str] = mapped_column(String, default="Moscow")
    # Time_To_Send
    tts: Mapped[str] = mapped_column(String, default="8:00")


async def initializator_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

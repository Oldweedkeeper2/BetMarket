import asyncio
from datetime import datetime, timedelta
from pytz import timezone

from sqlalchemy import Column, String, DateTime, BigInteger, Numeric, func, FetchedValue, Integer, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

from data.config import ALCHEMY_DATABASE_URL

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    username = Column(String, default='')
    surname = Column(String, default='')
    balance = Column(Numeric(8, 2), default=0)
    role = Column(String, default='User')
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp() + timedelta(hours=3))


class Product(Base):
    __tablename__ = 'products'
    id = Column(BigInteger, primary_key=True)
    name = Column(Text, nullable=False)
    price = Column(Numeric(8, 2), default=0)
    amount = Column(Integer, nullable=False)
    description = Column(Text, default='')
    uploader = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp() + timedelta(hours=3))


engine = create_async_engine(
        ALCHEMY_DATABASE_URL,
        echo=True,  # DEBUG  # включает логирование SQL-запросов (для отладки).
        pool_size=10,  # Минимальное количество соединений в пуле
        max_overflow=30  # Максимальное количество соединений в пуле
)
# Создание асинхронной сессии
AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
)


async def create_tables():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all, checkfirst=True)  # DEBUG MODE
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)


if __name__ == '__main__':
    asyncio.run(create_tables())

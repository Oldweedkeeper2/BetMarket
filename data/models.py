import asyncio
from datetime import timedelta

from sqlalchemy import Column, String, DateTime, BigInteger, Numeric, func, Integer, Text, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.testing.schema import Table

from data.config import ALCHEMY_DATABASE_URL

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    username = Column(String, default='')
    surname = Column(String, default='')
    balance = Column(Numeric(8, 2), default=0)
    phone = Column(String, default='')
    role = Column(String, default='User')
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp() + timedelta(hours=3))
    products = relationship("Product", back_populates="user")  # связь с продуктами
    orders = relationship("Order", back_populates="user")


# Вспомогательная таблица для связи многие ко многим между Order и Product
order_items = Table('order_items', Base.metadata,
                    Column('order_id', BigInteger, ForeignKey('orders.id'), primary_key=True),
                    Column('product_id', BigInteger, ForeignKey('products.id'), primary_key=True),
                    Column('quantity', Integer, nullable=False, default=1)
                    )


class Order(Base):
    __tablename__ = 'orders'
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp() + timedelta(hours=3))
    cart_sum = Column(Numeric(8, 2), default=0)
    
    user_id = Column(BigInteger, ForeignKey('users.id'))
    
    # Связь с User
    user = relationship("User", back_populates="orders")
    
    # Связь с Product через вспомогательную таблицу
    products = relationship("Product", secondary=order_items, back_populates="orders")


class Product(Base):
    __tablename__ = 'products'
    id = Column(BigInteger, primary_key=True)
    name = Column(Text, nullable=False)
    price = Column(Numeric(8, 2), default=0)
    amount = Column(Integer, default=0)
    description = Column(Text, default='')
    file_id = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp() + timedelta(hours=3))
    uploader_id = Column(BigInteger, ForeignKey('users.id'))
    user = relationship("User", back_populates="products")  # обратная связь с пользователем
    accounts = relationship("Account", back_populates="product")
    orders = relationship("Order", secondary=order_items, back_populates="products")


class Account(Base):
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True)
    account_name = Column(String, nullable=False)
    
    # Связь с Product
    product_id = Column(Integer, ForeignKey('products.id'))
    product = relationship("Product", back_populates="accounts")
    
    # Отношение с File
    files = relationship("File", back_populates="account", cascade="all, delete-orphan")


class File(Base):
    __tablename__ = 'files'
    
    id = Column(Integer, primary_key=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String)
    # Связь с Account
    account_id = Column(Integer, ForeignKey('accounts.id'))
    account = relationship("Account", back_populates="files")


engine = create_async_engine(
        ALCHEMY_DATABASE_URL,
        echo=True,  # DEBUG  # включает логирование SQL-запросов (для отладки).
        pool_size=10,  # Минимальное количество соединений в пуле
        max_overflow=50  # Максимальное количество соединений в пуле
)
# Создание асинхронной сессии
AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, checkfirst=True)  # DEBUG MODE
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)


if __name__ == '__main__':
    asyncio.run(create_tables())

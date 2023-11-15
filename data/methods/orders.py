import asyncio

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from typing import Union, List, Optional, Sequence

from sqlalchemy.orm import joinedload

from data.models import AsyncSessionLocal, Order, Product, Account


class OrderSQL:
    @classmethod
    async def add(cls, order_data: dict) -> Union[Order, None]:
        """
        Добавление нового заказа.
        """
        try:
            async with AsyncSessionLocal() as session:  # type: AsyncSession
                new_order = Order(**order_data)
                session.add(new_order)
                await session.commit()
                return new_order
        except SQLAlchemyError as e:
            await session.rollback()
            return None
    
    @classmethod
    async def delete_by_id(cls, id: int) -> Union[bool, Exception]:
        """
        Удаление заказа по идентификатору.
        """
        try:
            async with AsyncSessionLocal() as session:  # type: AsyncSession
                await session.execute(delete(Order).where(Order.id == id))
                await session.commit()
                return True
        except SQLAlchemyError as e:
            await session.rollback()
            return False
    
    @classmethod
    async def update(cls, id: int, update_data: dict) -> Union[Optional[Order], bool]:
        """
        Обновление данных заказа.
        """
        try:
            async with AsyncSessionLocal() as session:  # type: AsyncSession
                await session.execute(update(Order).where(Order.id == id).values(**update_data))
                await session.commit()
                
                result = await session.execute(select(Order).where(Order.id == id))
                updated_order = result.scalar_one_or_none()
                return updated_order
        except SQLAlchemyError as e:
            await session.rollback()
            return False
    
    @classmethod
    async def get_by_id(cls, id: int) -> None:
        try:
            async with AsyncSessionLocal() as session:  # type: AsyncSession
                result = await session.execute(select(Order)
                                               .options(joinedload(Order.products),
                                                        joinedload(Order.user))
                                               .where(Order.id == id))
                order = result.scalar_one_or_none()
                return order
        except SQLAlchemyError as e:
            await session.rollback()
            return None
    
    @classmethod
    async def get_all(cls) -> Sequence[Order] | SQLAlchemyError:  # изменить типирование
        try:
            async with AsyncSessionLocal() as session:  # type: AsyncSession
                result = await session.execute(select(Order)
                                               .options(joinedload(Order.products),
                                                        joinedload(Order.user)))
                orders = result.scalars().all()
                print('orders', orders)
                return orders
        except SQLAlchemyError as e:
            await session.rollback()
            return []

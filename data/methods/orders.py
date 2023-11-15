from typing import Union, Optional, Sequence

from sqlalchemy import select, update, delete, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from data.models import AsyncSessionLocal, Order, order_items


class OrderSQL:
    @classmethod
    def create_order_model(cls, user_id: int, cart_sum: float) -> Order:
        return Order(
                user_id=user_id,
                cart_sum=cart_sum
        )
    
    @classmethod
    async def add(cls, user_id: int, cart_sum: float, cart_items: dict) -> Union[Order, None]:
        async with AsyncSessionLocal() as session:  # type: AsyncSession
            try:
                # Создание заказа
                new_order = cls.create_order_model(user_id, cart_sum)
                session.add(new_order)
                await session.flush()  # Получаем order_id для нового заказа
                
                # Добавление элементов заказа
                for product_id, quantity in cart_items.items():
                    await session.execute(
                            insert(order_items).values(
                                    order_id=new_order.id,
                                    product_id=product_id,
                                    quantity=quantity
                            )
                    )
                
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

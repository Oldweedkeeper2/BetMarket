import logging
from typing import Union, List, Sequence, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from data.models import AsyncSessionLocal, Product, Account


class ProductSQL:
    @classmethod
    def create_product_model(cls, product: Dict) -> Union[Product, Exception]:
        name = product.get('name', None)
        price = product.get('price', None)
        amount = product.get('amount', 0)
        description = product.get('description', None)
        uploader_id = product.get('uploader_id', None)
        file_id = product.get('file_id', None)
        
        return Product(
                name=name,
                price=price,
                amount=amount,
                description=description,
                uploader_id=uploader_id,
                file_id=file_id,
        )
    
    @classmethod
    async def get_all_product(cls) -> Sequence[Product] | List:
        try:
            async with AsyncSessionLocal() as session:  # type: AsyncSession
                # Модифицируем запрос для включения связанных аккаунтов и файлов
                result = await session.execute(
                        select(Product).options(joinedload(Product.accounts).selectinload(Account.files))
                )
                products = result.unique().scalars().all()
                print('products', products)
                return products
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            await session.rollback()
            return []
    
    @classmethod
    async def get_by_id(cls, id: int) -> Product | None:
        try:
            async with AsyncSessionLocal() as session:  # type: AsyncSession
                result = await session.execute(
                        select(Product)
                        .where(Product.id == id)
                        .options(joinedload(Product.accounts).joinedload(Account.files))
                )
                # Использование unique() для предотвращения дублирования записей
                product = result.unique().scalar_one_or_none()
                return product
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            await session.rollback()
            return None
    
    @classmethod
    async def add(cls, product_data: Dict) -> Product | bool:
        async with AsyncSessionLocal() as session:  # type: AsyncSession
            try:
                new_product_model = cls.create_product_model(product_data)
                session.add(new_product_model)
                await session.commit()
                return new_product_model
            except Exception as e:
                print(f"An error occurred: {e}")
                await session.rollback()
                return False
    
    @classmethod
    async def get_cart_sum(cls, cart_items: Dict) -> float:
        async with AsyncSessionLocal() as session:  # type: AsyncSession
            try:
                result = await session.execute(select(Product)
                                               .where(Product.id.in_(cart_items.keys())))
                result = result.scalars()
                sum_result = sum([float(product.price * cart_items[product.id]) for product in result])  # type: float
                return sum_result
            except Exception as e:
                print(f"An error occurred: {e}")
                logging.debug(f"An error occurred: {e}")
                await session.rollback()
                return 0.0  # Возвращаем 0.0 в случае ошибки
    
    @classmethod
    async def update_product_amount(cls, product_id: int, amount: int, is_add: bool = False) -> bool:
        async with AsyncSessionLocal() as session:
            try:
                # Используем select for update для блокировки строки на время транзакции
                result = await session.execute(
                        select(Product).where(Product.id == product_id).with_for_update()
                )
                product = result.scalar_one()
                
                if product:
                    product.amount += amount if is_add else amount  # Увеличиваем количество
                    print('product.amount', product.amount)
                    await session.commit()
                    return True
                else:
                    await session.rollback()
                    return False
            except Exception as e:
                logging.debug(f"An error occurred while updating product amount: {e}")
                await session.rollback()
                return False

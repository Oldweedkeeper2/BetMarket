from data.models import AsyncSessionLocal, Product

import asyncio
from typing import Union, List, Sequence, Any, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ProductSQL:
    @classmethod
    def create_user_model(cls, product: Dict) -> Union[Product, Exception]:
        id = product.get('id', None)
        name = product.get('name', None)
        price = product.get('price', None)
        amount = product.get('amount', None)
        description = product.get('description', None)
        uploader = product.get('uploader', None)
        created_at = product.get('created_at', None)
        username = product.get('username', None)
        
        if id is None:
            return Exception('id is None')
        
        return Product(
                id=id,
                name=name,
                price=price,
                amount=amount,
                description=description,
                uploader=uploader,
                created_at=created_at,
                username=username,
        
        )
    
    @classmethod
    async def get_all_product(cls) -> Sequence[Product] | List:
        try:
            async with AsyncSessionLocal() as session:  # type: AsyncSession
                result = await session.execute(select(Product))
                products = result.scalars().all()
                return products
        except Exception as e:
            print(f"An error occurred: {e}")
            await session.rollback()
            return []

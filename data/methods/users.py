import asyncio
import logging
from typing import Union, List, Sequence, Any, Dict

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from data.models import AsyncSessionLocal, User


class UserSQL:
    @classmethod
    def create_user_model(cls, user: Dict) -> Union[User, Exception]:
        id = user.get('id', None)
        username = user.get('username', None)
        surname = user.get('surname', None)
        balance = user.get('balance', None)
        phone = user.get('phone', None)
        role = user.get('role', None)
        
        if id is None:
            return Exception('id is None')
        
        return User(
                id=id,
                username=username,
                surname=surname,
                balance=balance,
                phone=phone,
                role=role,
        )
    
    @classmethod
    async def get_all_admin(cls) -> List[User] | List:
        try:
            async with AsyncSessionLocal() as session:  # type: AsyncSession
                result = await session.execute(
                        select(User.id).where(User.role == 'Admin'))  # Укажи параметр, определяющий роль админа
                user_ids = list(result.scalars())
                return user_ids
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            await session.rollback()
            return []
    
    @classmethod
    async def get_all_manager_ids(cls) -> List[User] | List:
        try:
            async with AsyncSessionLocal() as session:  # type: AsyncSession
                result = await session.execute(
                        select(User.id).where(User.role == 'Manager'))  # Укажи параметр, определяющий роль админа
                user_ids = list(result.scalars())
                return user_ids
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            await session.rollback()
            return []
    
    @classmethod
    async def get_all_managers(cls) -> List[User] | List:
        try:
            async with AsyncSessionLocal() as session:  # type: AsyncSession
                result = await session.execute(
                        select(User).where(User.role == 'Manager'))  # Укажи параметр, определяющий роль админа
                managers = list(result.scalars())
                return managers
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            await session.rollback()
            return []
    
    @classmethod
    async def get_all(cls) -> Sequence[User] | list[Any]:
        try:
            async with AsyncSessionLocal() as session:  # type: AsyncSession
                result = await session.execute(select(User))
                users = result.scalars().all()
                return users
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            await session.rollback()
            return []
    
    @classmethod
    async def get_by_id(cls, id: int) -> Union[User, None]:
        try:
            async with AsyncSessionLocal() as session:  # type: AsyncSession
                result = await session.execute(select(User).where(User.id == id))
                user = result.scalar_one_or_none()
                return user
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            return None
    
    @classmethod
    async def get_by_username(cls, username: str) -> Union[User, None]:
        try:
            async with AsyncSessionLocal() as session:  # type: AsyncSession
                result = await session.execute(select(User).where(User.username == username))
                user = result.scalar_one_or_none()
                return user
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            return None
    
    @classmethod
    async def add(cls, user_data: Dict) -> bool:
        async with AsyncSessionLocal() as session:  # type: AsyncSession
            try:
                new_user_model = cls.create_user_model(user_data)
                existing_user = await cls.get_by_id(new_user_model.id)
                if not existing_user:
                    session.add(new_user_model)
                    await session.commit()
                    return True
                return False
            except Exception as e:
                logging.debug(f"An error occurred: {e}")
                await session.rollback()
                return False
    
    @classmethod
    async def update_role(cls, id: int, role: str) -> bool:
        async with AsyncSessionLocal() as session:  # type: AsyncSession
            try:
                existing_user = await cls.get_by_id(id)
                if not existing_user:
                    await session.rollback()
                    return False
                stmt = (
                    update(User)
                    .where(User.id == id)
                    .values(role=role)
                )
                await session.execute(stmt)
                await session.commit()
                return True
            except Exception as e:
                logging.debug(f"An error occurred: {e}")
                await session.rollback()
                return False
    
    @classmethod
    async def update_balance(cls, id: int, amount: float) -> bool | User:
        async with (AsyncSessionLocal() as session):  # type: AsyncSession
            try:
                existing_user = await cls.get_by_id(id)
                if not existing_user:
                    await session.rollback()
                    return False
                stmt = (
                    update(User)
                    .where(User.id == id)
                    .values(balance=User.balance + amount)
                )
                await session.execute(stmt)
                await session.commit()
                return True
            except Exception as e:
                logging.debug(f"An error occurred: {e}")
                await session.rollback()
                return False
    
    @classmethod
    async def update_banned(cls, id: int, banned: bool) -> bool | User:
        async with AsyncSessionLocal() as session:  # type: AsyncSession
            try:
                stmt = (
                    update(User)
                    .where(User.id == id)
                    .values(banned=banned)
                )
                await session.execute(stmt)
                await session.commit()
                return True
            except Exception as e:
                logging.debug(f"An error occurred: {e}")
                await session.rollback()
                return False
    
    @classmethod
    async def delete(cls, id: int) -> bool:
        async with AsyncSessionLocal() as session:  # type: AsyncSession
            try:
                existing_user = await cls.get_by_id(id)
                if not existing_user:
                    await session.delete(existing_user)
                    await session.commit()
                    return True
                return False
            except Exception as e:
                logging.debug(f"An error occurred: {e}")
                await session.rollback()
                return False


if __name__ == '__main__':
    asyncio.run(UserSQL.add(
            {'id': 823932122, 'username': 'Oldweedkeeper', 'surname': 'Developer', 'balance': 1000, 'role': 'Admin'}))

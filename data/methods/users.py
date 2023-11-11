import asyncio
from typing import Union, List, Sequence, Any, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data.models import AsyncSessionLocal, User


class UserSQL:
    @classmethod
    def create_user_model(cls, user: Dict) -> Union[User, Exception]:
        id = user.get('id', None)
        username = user.get('username', None)
        surname = user.get('surname', None)
        balance = user.get('balance', None)
        role = user.get('role', None)
        
        if id is None:
            return Exception('id is None')
        
        return User(
                id=id,
                username=username,
                surname=surname,
                balance=balance,
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
            print(f"An error occurred: {e}")
            await session.rollback()
            return []
    
    @classmethod
    async def get_all_manager(cls) -> List[User] | List:
        try:
            async with AsyncSessionLocal() as session:  # type: AsyncSession
                result = await session.execute(
                        select(User.id).where(User.role == 'Manager'))  # Укажи параметр, определяющий роль админа
                user_ids = list(result.scalars())
                return user_ids
        except Exception as e:
            print(f"An error occurred: {e}")
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
            print(f"An error occurred: {e}")
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
            print(f"An error occurred: {e}")
            return None
    
    @classmethod
    async def add(cls, user_data: Dict) -> bool:
        async with AsyncSessionLocal() as session:  # type: AsyncSession
            try:
                new_user_model = cls.create_user_model(user_data)
                existing_user = await cls.get_by_id(new_user_model.id)
                print(new_user_model.id, new_user_model.role, new_user_model.balance)
                if not existing_user:
                    session.add(new_user_model)
                    await session.commit()
                    return True
                return False
            except Exception as e:
                print(f"An error occurred: {e}")
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
                print(f"An error occurred: {e}")
                await session.rollback()
                return False


if __name__ == '__main__':
    asyncio.run(UserSQL.add((823932122, 'Oldweedkeeper', 'Developer', '1000', 'Admin')))

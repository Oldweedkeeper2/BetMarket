import logging
from typing import Dict, Sequence, List, Union

from sqlalchemy import delete, select

from data.models import AsyncSessionLocal, Account


class AccountSQL:
    @classmethod
    def create_account_model(cls, account_data: Dict) -> Union[Account, Exception]:
        account_name = account_data.get('account_name')
        product_id = account_data.get('product_id')
        
        return Account(
                account_name=account_name,
                product_id=product_id
        )
    
    @classmethod
    async def get_all_accounts(cls) -> Sequence[Account] | List:
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(Account))
                accounts = result.scalars().all()
                return accounts
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            await session.rollback()
            return []
    
    @classmethod
    async def get_account_by_id(cls, id: int) -> Account | None:
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(Account).where(Account.id == id))
                account = result.scalar_one_or_none()
                return account
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            await session.rollback()
            return None
    
    @classmethod
    async def add_account(cls, account_data: Dict) -> int | bool:
        async with AsyncSessionLocal() as session:
            try:
                new_account = cls.create_account_model(account_data)
                session.add(new_account)
                await session.commit()
                return new_account.id
            except Exception as e:
                logging.debug(f"An error occurred: {e}")
                await session.rollback()
                return False
    
    @classmethod
    async def delete_account(cls, id: int) -> bool:
        async with AsyncSessionLocal() as session:
            try:
                await session.execute(delete(Account).where(Account.id == id))
                await session.commit()
                return True
            except Exception as e:
                logging.debug(f"An error occurred: {e}")
                await session.rollback()
                return False
    
    @classmethod
    async def add_accounts(cls, product_id: int, accounts_data: List[Dict]) -> bool:
        async with AsyncSessionLocal() as session:
            try:
                for account_data in accounts_data:
                    new_account = Account(
                            account_name=account_data.get('account_name'),
                            product_id=product_id
                    )
                    session.add(new_account)
                
                await session.commit()
                return True
            except Exception as e:
                logging.debug(f"An error occurred while adding accounts: {e}")
                await session.rollback()
                return False

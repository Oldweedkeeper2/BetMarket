import logging
from typing import Dict, Sequence, List, Union

from sqlalchemy import delete, select

from data.models import AsyncSessionLocal, File


class FileSQL:
    @classmethod
    def create_file_model(cls, file_data: Dict) -> Union[File, Exception]:
        file_name = file_data.get('file_name')
        file_path = file_data.get('file_path')
        file_type = file_data.get('file_type')
        account_id = file_data.get('account_id')
        
        return File(
                file_name=file_name,
                file_path=file_path,
                file_type=file_type,
                account_id=account_id
        )
    
    @classmethod
    async def get_all_files(cls) -> Sequence[File] | List:
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(File))
                files = result.scalars().all()
                return files
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            await session.rollback()
            return []
    
    @classmethod
    async def get_file_by_id(cls, id: int) -> File | None:
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(File).where(File.id == id))
                file = result.scalar_one_or_none()
                return file
        except Exception as e:
            logging.debug(f"An error occurred: {e}")
            await session.rollback()
            return None
    
    @classmethod
    async def add_file(cls, file_data: Dict) -> int | bool:
        async with AsyncSessionLocal() as session:
            try:
                new_file = cls.create_file_model(file_data)
                session.add(new_file)
                await session.commit()
                return new_file.id
            except Exception as e:
                logging.debug(f"An error occurred: {e}")
                await session.rollback()
                return False
    
    @classmethod
    async def delete_file(cls, id: int) -> bool:
        async with AsyncSessionLocal() as session:
            try:
                await session.execute(delete(File).where(File.id == id))
                await session.commit()
                return True
            except Exception as e:
                logging.debug(f"An error occurred: {e}")
                await session.rollback()
                return False
    
    @classmethod
    async def add_files(cls, account_id: int, files_data: List[Dict]) -> bool:
        async with AsyncSessionLocal() as session:
            try:
                for file_data in files_data:
                    new_file = File(
                            file_name=file_data.get('file_name'),
                            file_path=file_data.get('file_path'),
                            file_type=file_data.get('file_type'),
                            account_id=account_id
                    )
                    session.add(new_file)
                
                await session.commit()
                return True
            except Exception as e:
                logging.debug(f"An error occurred while adding files: {e}")
                await session.rollback()
                return False
    
    # @classmethod
    # async def get

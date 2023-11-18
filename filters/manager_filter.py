from aiogram.filters import BaseFilter
from aiogram.types import Message

from data.methods.users import UserSQL


class ManagerFilter(BaseFilter):
    
    async def __call__(self, message: Message) -> bool:
        manager_ids_list = await UserSQL.get_all_manager_ids()
        user_id = message.from_user.id
        return user_id in manager_ids_list

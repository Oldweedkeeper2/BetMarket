from aiogram.filters import BaseFilter
from aiogram.types import Message

from data.methods.users import UserSQL


class AdminFilter(BaseFilter):
    
    async def __call__(self, message: Message) -> bool:
        admin_ids_list = await UserSQL.get_all_admin()
        user_id = message.from_user.id
        return user_id in admin_ids_list

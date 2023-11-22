from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from data.methods.users import UserSQL


class AdminFilter(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        admin_ids_list = await UserSQL.get_all_admin()
        if isinstance(event, CallbackQuery):
            user_id = event.message.chat.id
        else:
            user_id = event.from_user.id
      
        return user_id in admin_ids_list
        
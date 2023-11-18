import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message

from data.methods.users import UserSQL


class BannedUserFilter(BaseFilter):
    
    async def __call__(self, message: Message) -> bool:
        user = await UserSQL.get_by_id(int(message.from_user.id))
        logging.debug(user.banned)
        return True if not user.banned else False

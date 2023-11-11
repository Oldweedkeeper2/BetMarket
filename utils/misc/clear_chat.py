from contextlib import suppress

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message


async def clear_chat(data: dict, chat_id: int) -> None:
    data.setdefault('items_to_del', [])
    if 'items_to_del' in data.keys():
        for msg in data['items_to_del']:  # type: Message
            with suppress(TelegramBadRequest):
                await msg.bot.delete_message(chat_id=chat_id,
                                             message_id=msg.message_id)
        data['items_to_del'] = []

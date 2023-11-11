from contextlib import suppress

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message
import logging


async def clear_chat(data: dict) -> None:
    data.setdefault('items_to_del', [])
    if 'items_to_del' in data.keys():
        print('data', data)
        for msg in data['items_to_del']:  # type: Message
            print(msg)
            try:
                await msg.bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
            except TelegramBadRequest as e:
                logging.warning(f"Error deleting message: {e}")
        data['items_to_del'] = []

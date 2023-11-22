from typing import Any

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from data.config import TECH_SUPPORT_USERNAME
from keyboards.inline.help import get_help_keyboard
from utils.misc.clear_chat import clear_chat

router = Router()


@router.callback_query(F.data == "help")
async def handle(call: CallbackQuery, state: FSMContext) -> Any:
    await handle_help(message=call.message, state=state)


@router.message(Command('help'))
async def handle(message: Message, state: FSMContext) -> Any:
    await handle_help(message=message, state=state)
    await message.delete()


async def handle_help(message: Message, state: FSMContext):
    msg = await message.answer(
            text="<b>ТЕКСТ ДЛЯ ПОМОЩИ ЗАБЛУБИВШИМСЯ ИЛИ ДЕБИЛАМ\n\n</b>"
                 f"<b>Лучше всего поставить также контакты менеджера @{TECH_SUPPORT_USERNAME}</b>",
            reply_markup=get_help_keyboard()
    )
    data = await state.get_data()
    await clear_chat(data=data)
    data['items_to_del'].append(msg)
    await state.update_data(data)

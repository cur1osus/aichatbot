from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from bot.states import UserState

from bot.db.models import UserDB, ChatDB, MessageDB
from bot.utils import fn

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import Message
    from sqlalchemy.ext.asyncio import AsyncSession


router = Router()
logger = logging.getLogger(__name__)


@router.message(Command(commands=["new_chat"]))
async def new_chat(
    message: Message,
    user: UserDB,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    await message.answer("Введите ваш вопрос:")
    await state.set_state(UserState.enter_question)


@router.message(UserState.enter_question)
async def get_question(
    message: Message,
    user: UserDB,
    session: AsyncSession,
    state: FSMContext,
) -> None:
    state_data = await state.get_data()

    question = message.text or ""

    if r := state_data.get("chat_id"):
        chat = await session.get(ChatDB, r) or ChatDB(chat_name=question)
    else:
        chat = ChatDB(chat_name=question)

    messages = await chat.awaitable_attrs.messages

    chain_messages = fn.make_chain(raw_messages=messages, question=question)
    answer = fn.get_answer(chain_messages)

    await message.answer(answer, parse_mode="MarkdownV2")

    message_db = MessageDB(content=question, timestamp=datetime.now().timestamp(), role="user")
    message_db_from_assistant = MessageDB(content=answer, timestamp=datetime.now().timestamp(), role="assistant")
    chat.messages.append(message_db)
    chat.messages.append(message_db_from_assistant)
    if not state_data.get("chat_id"):
        user.chats.append(chat)

    await session.commit()

    await state.update_data(chat_id=chat.id)

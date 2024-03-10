import asyncio

from pyrogram import Client
from pyrogram.types import Message

from orm.core import AsyncCore
from src.enum.last_state import State
from src.plugins.services.start import start_handler
from src.plugins.services.task import start_task_handler


async def login_handler(
        client: Client,
        user_tg_id: int,
        chat_id: int,
):
    await client.send_message(
        chat_id=chat_id,
        text="Enter your login"
    )
    await AsyncCore().set_session_state(
        user_tg_id=user_tg_id,
        state=State.LOGIN
    )


async def login_failed_enter_handler(
        client: Client,
        message: Message
):
    await client.send_message(
        chat_id=message.chat.id,
        text=f"Warning! Account with login {message.text} does not exist!"
    )
    await asyncio.sleep(1)
    await start_handler(
        client=client,
        message=message
    )


async def login_enter_handler(
        client: Client,
        message: Message
):
    account = await AsyncCore().execute_account(message.text)
    await client.send_message(
        chat_id=message.chat.id,
        text=f"Hello {account.name}!"
    )
    await AsyncCore().set_session_state(
        account_id=account.id,
        user_tg_id=message.from_user.id,
        state=State.TASKS
    )
    await asyncio.sleep(1)
    await start_task_handler(
        client=client,
        message=message
    )

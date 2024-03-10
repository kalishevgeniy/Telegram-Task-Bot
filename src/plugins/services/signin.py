from pyrogram import Client
from pyrogram.types import Message

from orm.core import AsyncCore
from src.enum.last_state import State
from src.plugins.controllers.start import start_controller


async def signin_handler(
        client: Client,
        chat_id: int
):
    await client.send_message(
        chat_id=chat_id,
        text="For create user, please enter login"
    )
    await AsyncCore().set_session_state(
        state=State.REGISTER_LOGIN,
        user_tg_id=chat_id
    )


async def signin_login_controller(
        client: Client,
        message: Message
):
    await client.send_message(
        chat_id=message.chat.id,
        text=f"User with login {message.text} create. Now enter your name."
    )

    await AsyncCore().create_account(
        login_account=message.text
    )
    await AsyncCore().set_session_state(
        State.REGISTER_NAME,
        user_tg_id=message.from_user.id,
        last_value=message.text
    )


async def signin_login_forbidden_handler(
        client: Client,
        message: Message
):
    await client.send_message(
        chat_id=message.chat.id,
        text=f"Warning! User with login {message.text} already exist!"
    )
    await signin_handler(
        client=client,
        chat_id=message.chat.id
    )


async def signin_name_handler(
        client: Client,
        message: Message
):
    curr_value = await AsyncCore().execute_current_state(
        user_tg_id=message.from_user.id,
    )
    await client.send_message(
        chat_id=message.chat.id,
        text=f"User {message.text} created!"
    )
    await AsyncCore().update_account(
        name_account=message.text,
        login_account=curr_value.last_value if curr_value else None
    )

    await AsyncCore().set_session_state(
        State.REGISTER_NAME,
        user_tg_id=message.from_user.id,
        last_value=message.text
    )
    await start_controller(client, message)

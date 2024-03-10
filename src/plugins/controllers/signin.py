from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery

from src.enum.last_state import State
from src.filters.account import account_exist
from src.filters.router import router_filter
from src.filters.state import current_state_filter
from src.plugins.services.signin import (
    signin_handler,
    signin_login_controller,
    signin_name_handler,
    signin_login_forbidden_handler
)


@Client.on_callback_query(
    router_filter('signin')
)
async def signin_inline_controller(
        client: Client,
        callback_query: CallbackQuery
):
    """
    Inline command button "sign in"
    and enter your login name
    """
    await signin_handler(
        client=client,
        chat_id=callback_query.from_user.id
    )
    await client.answer_callback_query(callback_query.id)


@Client.on_message(
    filters.command(commands="signin", prefixes='/')
)
async def signin_controller(
        client: Client,
        message: Message
):
    """
    Start logging process after command /signin
    and enter your login name
    """
    await signin_handler(
        client=client,
        chat_id=message.from_user.id
    )


@Client.on_message(
    current_state_filter(State.REGISTER_LOGIN)
    &
    ~account_exist
)
async def signin_login_handler(
        client: Client,
        message: Message
):
    """
    Check login in db and create account
    """
    await signin_login_controller(
        client=client,
        message=message
    )


@Client.on_message(
    current_state_filter(State.REGISTER_LOGIN)
    &
    account_exist
)
async def signin_login_forbidden_controller(
        client: Client,
        message: Message
):
    """
    Account already exist in db
    Enter new account login
    """
    await signin_login_forbidden_handler(
        client=client,
        message=message
    )


@Client.on_message(
    current_state_filter(State.REGISTER_NAME)
)
async def signin_name_controller(
        client: Client,
        message: Message
):
    """
    For account enter name
    """
    await signin_name_handler(
        client=client,
        message=message
    )

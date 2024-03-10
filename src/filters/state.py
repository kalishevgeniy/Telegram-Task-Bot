from typing import Union

from pyrogram import filters
from pyrogram.types import Message, CallbackQuery

from orm.core import AsyncCore


def current_state_filter(data):
    async def func(
            flt,
            _,
            pyrogram_message: Union[Message, CallbackQuery]
    ):
        """
        This is filter use for check current state of the chat

        :param flt:
        :param _:
        :param pyrogram_message:
        :return: Bool
        """
        if isinstance(pyrogram_message, Message):
            user_tg_id = pyrogram_message.chat.id
        else:
            user_tg_id = pyrogram_message.from_user.id

        result = await AsyncCore().execute_current_state(user_tg_id=user_tg_id)
        return flt.data == result.last_state if result else False
    return filters.create(func, data=data)

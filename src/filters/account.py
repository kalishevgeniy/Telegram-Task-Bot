from pyrogram import filters
from pyrogram.types import Message

from orm.core import AsyncCore


async def func(_, __, message: Message):
    result = await AsyncCore().execute_account(message.text)
    return message.text == result.login if result else False

account_exist = filters.create(func)

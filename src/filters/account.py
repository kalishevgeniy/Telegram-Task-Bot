from pyrogram import filters
from pyrogram.types import Message

from orm.core import AsyncCore


async def func(_, __, message: Message):
    """
    Filter for check exists account in db

    :param _:
    :param __:
    :param message: message with text attr. By this text find login in db
    :return:
    """
    result = await AsyncCore().execute_account(login_account=message.text)
    return message.text == result.login if result else False

account_exist = filters.create(func)

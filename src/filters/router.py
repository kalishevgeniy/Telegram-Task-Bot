from pyrogram import filters
from pyrogram.types import CallbackQuery


def router_filter(data):
    async def func(flt, _, query: CallbackQuery):
        """
        Choose controller by callback_data in inline menu in bot

        :param flt: filter func
        :param _:
        :param query: CallbackQuery
        :return: Bool
        """
        return flt.data == query.data
    return filters.create(func, data=data)

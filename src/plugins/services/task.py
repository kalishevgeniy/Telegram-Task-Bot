import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode

from orm.core import AsyncCore
from src.enum.last_state import State

from src.plugins.buttons.task import (
    get_list_tasks_button, choose_task_button, logout_button,
    create_task_button, edit_button, delete_button, back_button,
    back_to_task_button, edit_description_button,
    edit_name_button
)
from src.plugins.controllers.start import start_controller


async def start_task_handler(client: Client, message: Message):
    await client.send_message(
        message.chat.id,
        text="For management task choose button",
        reply_markup=InlineKeyboardMarkup(
            [
                [get_list_tasks_button, create_task_button],
                [choose_task_button],
                [logout_button]
            ]
        ),
        parse_mode=ParseMode.MARKDOWN
    )


async def logout_task_handler(
        client: Client,
        message: Message
):
    await AsyncCore().set_session_state(
        state=State.START,
        user_tg_id=message.chat.id,
    )
    await start_controller(
        client=client,
        message=message
    )


async def create_task_handler(
        client: Client,
        callback_query: CallbackQuery
):
    await client.send_message(
        chat_id=callback_query.message.chat.id,
        text="Enter task name"
    )
    await AsyncCore().set_session_state(
        state=State.TASKS_CREATE_NAME,
        user_tg_id=callback_query.from_user.id,
    )
    await client.answer_callback_query(callback_query.id)


async def create_task_name_handler(client: Client, message: Message):
    await client.send_message(
        chat_id=message.chat.id,
        text=f"Enter tasks description"
    )
    await AsyncCore().set_session_state(
        State.TASKS_CREATE_DESCRIPTION,
        user_tg_id=message.from_user.id,
        last_value=message.text
    )
    await AsyncCore().create_task(
        name=message.text,
        user_tg_id=message.from_user.id
    )


async def create_task_description_handler(client: Client, message: Message):
    task = await AsyncCore().execute_task(
        user_tg_id=message.from_user.id
    )
    await client.send_message(
        chat_id=message.chat.id,
        text=f"Task create!"
    )

    await AsyncCore().update_tasks(
        task_id=task.id,
        name=task.name,
        description=message.text,
        is_complete=False
    )
    await asyncio.sleep(1)
    await AsyncCore().set_session_state(
        State.TASKS,
        user_tg_id=message.from_user.id,
        last_value=message.text
    )
    await start_task_handler(
        client=client,
        message=message
    )


async def get_task_handler(
        client: Client,
        callback_query: CallbackQuery
):
    tasks = await AsyncCore().execute_tasks(
        user_tg_id=callback_query.from_user.id
    )

    if tasks:
        sting_tasks = ''.join([
            f"{task.id}. - {task.name} \n" for task in tasks
        ])
        await callback_query.message.reply(
            text=f"Current tasks: ```\n{sting_tasks}```"
        )
    else:
        await callback_query.message.reply(
            text="You dont have tasks =)"
        )

    await client.answer_callback_query(callback_query.id)


async def choose_task_handler(
        client: Client,
        callback_query: CallbackQuery
):

    await client.send_message(
        chat_id=callback_query.message.chat.id,
        text=f"Enter ID task for edit/delete"
    )
    await AsyncCore().set_session_state(
        state=State.TASKS_CHOOSE,
        user_tg_id=callback_query.from_user.id,
        last_value=None
    )
    await client.answer_callback_query(callback_query.id)


async def work_with_task_handler(
        client: Client,
        message: Message
):
    task_id = int(message.text)
    task = await AsyncCore().execute_task(
        user_tg_id=message.chat.id,
        task_id=task_id
    )

    if not task:
        await client.send_message(
            message.chat.id,
            text=f"Task with ID {task_id} does not exist!",
        )
        await AsyncCore().set_session_state(
            State.TASKS,
            user_tg_id=message.chat.id,
            last_value=None
        )
        await asyncio.sleep(1)
        await start_task_handler(
            client=client,
            message=message
        )
        return

    change_status_button = InlineKeyboardButton(
        text="I haven't done task" if task.is_complete else "I have done task!",
        callback_data="change_status_task"
    )

    text = f"""```
ID -          {task.id}
Name -        {task.name}
Status -      {'✅' if task.is_complete else '❌'}
Description - {task.description}```
"""

    await client.send_message(
        message.chat.id,
        text=text + "What would you like to do with this task?",
        reply_markup=InlineKeyboardMarkup(
            [
                [edit_button, delete_button],
                [change_status_button],
                [back_button]
            ]
        ),
        parse_mode=ParseMode.MARKDOWN
    )

    await AsyncCore().set_session_state(
        state=State.TASKS_CHOOSE,
        user_tg_id=message.chat.id,
        last_value=message.text
    )


async def back_task_handler(
        client: Client,
        callback_query: CallbackQuery
):
    await AsyncCore().set_session_state(
        state=State.TASKS,
        user_tg_id=callback_query.from_user.id,
        last_value=None
    )
    await start_task_handler(
        client=client,
        message=callback_query.message
    )
    await client.answer_callback_query(callback_query.id)


async def delete_task_handler(
        client: Client,
        callback_query: CallbackQuery
):
    curr_state = await AsyncCore().execute_current_state(
        user_tg_id=callback_query.from_user.id
    )
    await AsyncCore().delete_task(int(curr_state.last_value))
    await client.send_message(
        callback_query.from_user.id,
        text=f"Task with ID {int(curr_state.last_value)} deleted!",
    )
    await AsyncCore().set_session_state(
        State.TASKS,
        user_tg_id=callback_query.from_user.id,
        last_value=None
    )
    await client.answer_callback_query(callback_query.id)
    await asyncio.sleep(1)
    await start_task_handler(
        client=client,
        message=callback_query.message
    )


async def change_status_task_handler(
        client: Client,
        callback_query: CallbackQuery
):
    curr_state = await AsyncCore().execute_current_state(
        user_tg_id=callback_query.from_user.id
    )

    task = await AsyncCore().execute_task(
        user_tg_id=callback_query.from_user.id,
        task_id=int(curr_state.last_value)
    )

    await AsyncCore().update_tasks(
        task_id=task.id,
        name=task.name,
        description=task.description,
        is_complete=not task.is_complete
    )

    await client.send_message(
        callback_query.message.chat.id,
        text=f"Task status with ID {int(curr_state.last_value)} updated!",
    )
    await client.answer_callback_query(callback_query.id)
    await asyncio.sleep(1)

    callback_query.message.text = curr_state.last_value
    await work_with_task_handler(
        client=client,
        message=callback_query.message
    )


async def edit_task_handler(
        client: Client,
        callback_query: CallbackQuery
):
    curr_state = await AsyncCore().execute_current_state(
        user_tg_id=callback_query.from_user.id
    )

    await client.send_message(
        callback_query.from_user.id,
        text="What you want change in task?",
        reply_markup=InlineKeyboardMarkup(
            [
                [edit_name_button],
                [edit_description_button],
                [back_to_task_button]
            ]
        )
    )
    await AsyncCore().set_session_state(
        state=State.TASK_EDIT,
        user_tg_id=callback_query.from_user.id,
        last_value=curr_state.last_value
    )
    await client.answer_callback_query(callback_query.id)


async def back_task_edit_handler(
        client: Client,
        callback_query: CallbackQuery
):
    curr_state = await AsyncCore().execute_current_state(
        user_tg_id=callback_query.from_user.id
    )

    await AsyncCore().set_session_state(
        state=State.TASKS_CHOOSE,
        user_tg_id=callback_query.from_user.id,
        last_value=curr_state.last_value
    )

    callback_query.message.text = curr_state.last_value
    await work_with_task_handler(
        client=client,
        message=callback_query.message
    )
    await client.answer_callback_query(callback_query.id)


async def name_task_edit_handler(
        client: Client,
        callback_query: CallbackQuery
):
    curr_state = await AsyncCore().execute_current_state(
        user_tg_id=callback_query.from_user.id
    )

    await client.send_message(
        callback_query.message.chat.id,
        text="Enter new task name",
    )

    await AsyncCore().set_session_state(
        state=State.TASK_EDIT_NAME,
        user_tg_id=callback_query.from_user.id,
        last_value=curr_state.last_value
    )
    await client.answer_callback_query(callback_query.id)


async def enter_name_task_edit_handler(
        client: Client,
        message: Message
):
    curr_state = await AsyncCore().execute_current_state(
        user_tg_id=message.from_user.id
    )
    task = await AsyncCore().execute_task(
        user_tg_id=message.from_user.id,
        task_id=int(curr_state.last_value)
    )

    await AsyncCore().update_tasks(
        task_id=task.id,
        name=message.text,
        description=task.description,
        is_complete=task.is_complete
    )
    await AsyncCore().set_session_state(
        state=State.TASKS_CHOOSE,
        user_tg_id=message.from_user.id,
        last_value=curr_state.last_value
    )
    message.text = curr_state.last_value
    await work_with_task_handler(client, message)


async def description_task_edit_handler(
        client: Client,
        callback_query: CallbackQuery
):
    curr_state = await AsyncCore().execute_current_state(
        user_tg_id=callback_query.from_user.id
    )

    await client.send_message(
        callback_query.message.chat.id,
        text="Enter new task description",
    )

    await AsyncCore().set_session_state(
        state=State.TASK_EDIT_DESCRIPTION,
        user_tg_id=callback_query.from_user.id,
        last_value=curr_state.last_value
    )
    await client.answer_callback_query(callback_query.id)


async def enter_description_task_edit_handler(
        client: Client,
        message: Message
):
    curr_state = await AsyncCore().execute_current_state(
        user_tg_id=message.from_user.id
    )
    task = await AsyncCore().execute_task(
        user_tg_id=message.from_user.id,
        task_id=int(curr_state.last_value)
    )
    await AsyncCore().update_tasks(
        task_id=task.id,
        name=task.name,
        description=message.text,
        is_complete=task.is_complete
    )
    await AsyncCore().set_session_state(
        state=State.TASKS_CHOOSE,
        user_tg_id=message.from_user.id,
        last_value=curr_state.last_value
    )
    message.text = curr_state.last_value
    await work_with_task_handler(client, message)

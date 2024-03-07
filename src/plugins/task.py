import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode

from orm.core import AsyncCore
from src.enum.last_state import State
from src.filters.account import account_exist
from src.filters.router import router_filter
from src.filters.state import current_state_filter
from src.plugins.start import command_start


@Client.on_message(
    filters.command(commands="tasks", prefixes='/')
    &
    current_state_filter(State.TASKS)
)
async def start_tasks(client: Client, message: Message):
    get_list_tasks_button = InlineKeyboardButton(
        text="Get current tasks",
        callback_data="current_tasks"
    )
    create_task_button = InlineKeyboardButton(
        text="Create new tasks",
        callback_data="create_task"
    )
    choose_task_button = InlineKeyboardButton(
        text="Choose task",
        callback_data="choose_task"
    )
    logout_button = InlineKeyboardButton(
        text="Logout",
        callback_data="logout"
    )

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


@Client.on_callback_query(
    router_filter('create_task')
    &
    current_state_filter(State.TASKS)
)
async def create_task_handler(client: Client, callback_query):
    await client.send_message(
        chat_id=callback_query.message.chat.id,
        text="Enter task name"
    )
    await AsyncCore().set_session_state(
        State.TASKS_CREATE_NAME,
        user_tg_id=callback_query.from_user.id,
    )


@Client.on_message(
    current_state_filter(State.TASKS_CREATE_NAME)
)
async def create_task_name_handler(client: Client, message: Message):
    await client.send_message(
        chat_id=message.chat.id,
        text=f"Enter tasks description"
    )
    await AsyncCore().set_session_state(
        State.TASKS_CREATE_DESCRIPTION,
        user_tg_id=message.chat.id,
        last_value=message.text
    )
    await AsyncCore().create_task(message.text, message.chat.id)


@Client.on_message(
    current_state_filter(State.TASKS_CREATE_DESCRIPTION)
)
async def create_task_description_handler(client: Client, message: Message):
    task = await AsyncCore().execute_task(message.chat.id)
    await client.send_message(
        chat_id=message.chat.id,
        text=f"Task create!"
    )

    await AsyncCore().update_tasks(task.id, message.text)
    await asyncio.sleep(1)
    await AsyncCore().set_session_state(
        State.TASKS,
        user_tg_id=message.chat.id,
        last_value=message.text
    )
    await start_tasks(client, message)


@Client.on_callback_query(
    router_filter('current_tasks')
    &
    current_state_filter(State.TASKS)
)
async def get_tasks_handler(client: Client, callback_query: CallbackQuery):
    tasks = await AsyncCore().execute_tasks(callback_query.from_user.id)

    if tasks:
        sting_tasks = ''.join([
            f"{task.id}. - {task.name} \n" for task in tasks
        ])
        await client.send_message(
            chat_id=callback_query.message.chat.id,
            text=f"Current tasks: ```\n{sting_tasks}```"
        )
    else:
        await client.send_message(
            chat_id=callback_query.message.chat.id,
            text="You dont have tasks =)"
        )


@Client.on_callback_query(
    router_filter('choose_task')
    &
    current_state_filter(State.TASKS)
)
async def choose_task_handler(client: Client, callback_query: CallbackQuery):

    await client.send_message(
        chat_id=callback_query.message.chat.id,
        text=f"Enter ID task for edit/delete"
    )
    await AsyncCore().set_session_state(
        State.TASKS_CHOOSE,
        user_tg_id=callback_query.from_user.id,
        last_value=None
    )


@Client.on_message(
    current_state_filter(State.TASKS_CHOOSE)
)
async def work_with_task_handler(client: Client, message: Message):
    task_id = int(message.text)
    task = await AsyncCore().execute_task(message.chat.id, task_id=task_id)

    edit_button = InlineKeyboardButton(
        text="Edit task",
        callback_data="edit_task"
    )
    delete_button = InlineKeyboardButton(
        text="Delete task",
        callback_data="delete_task"
    )
    complete_button = InlineKeyboardButton(
        text="I done task!" if task.is_complete else "I didn't do task =(",
        callback_data="complete_task"
    )
    back_button = InlineKeyboardButton(
        text="Back",
        callback_data="back_task"
    )

    text = f"""```
ID -          {task.id}
Name -        {task.name}
Status -      {'✅' if task.is_complete else '❌'}
Description - {task.description}
    ```"""
    await client.send_message(
        message.chat.id,
        text=text + "What would you like to do with this task?",
        reply_markup=InlineKeyboardMarkup(
            [
                [edit_button, delete_button],
                [complete_button],
                [back_button]
            ]
        ),
        parse_mode=ParseMode.MARKDOWN
    )

    await AsyncCore().set_session_state(
        State.TASKS_CHOOSE,
        user_tg_id=message.chat.id,
        last_value=message.text
    )


@Client.on_callback_query(
    router_filter('back_task')
    &
    current_state_filter(State.TASKS_CHOOSE)
)
async def back_task_handler(client: Client, callback_query: CallbackQuery):
    await AsyncCore().set_session_state(
        State.TASKS,
        user_tg_id=callback_query.from_user.id,
        last_value=None
    )
    await start_tasks(client, callback_query.message)


@Client.on_callback_query(
    router_filter('delete_task')
    &
    current_state_filter(State.TASKS_CHOOSE)
)
async def delete_task_handler(client: Client, callback_query: CallbackQuery):
    curr_state = await AsyncCore().execute_current_state(
        callback_query.from_user.id
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
    await asyncio.sleep(1)
    await start_tasks()



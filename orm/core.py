from pyrogram import Client
from pyrogram.types import Message, CallbackQuery
from sqlalchemy import select, update, delete, and_

from orm.engine import async_engine, async_session_factory
from orm.models import Base, Users, Sessions, Accounts, Tasks
from src.enum.last_state import State
from src.models import SessionsPydantic, AccountsPydantic, TasksPydantic


class AsyncCore:

    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def start(_: Client, message: Message):
        async with async_session_factory() as session:
            user = await session.execute(
                select(Users).where(
                    Users.tg_id == message.chat.id
                )
            )
            user = user.scalar_one_or_none()
            if not user:
                user = Users(
                    tg_id=message.chat.id,
                    first_name=message.chat.first_name,
                    last_name=message.chat.last_name
                )
                session.add(user)
                await session.flush()

                tg_session = Sessions(
                    user_id=user.id,
                    last_state=State.START,
                )
                session.add(tg_session)
            else:
                await session.execute(
                    update(Sessions)
                    .values(
                        last_state=State.START,
                        last_value=None
                    )
                    .where(Sessions.user_id == user.id)
                )

            await session.commit()

    @staticmethod
    async def execute_current_state(user_tg_id: int) -> SessionsPydantic:
        """
        SELECT sessions.last_state
        FROM users
        INNER JOIN sessions ON user.id = sessions.user_id
        WHERE user.tg_id = $1::int;

        :param user_tg_id:
        :return:
        """
        async with async_session_factory() as session:
            query = (
                select(Sessions).
                select_from(Users).
                join(Sessions, Users.id == Sessions.user_id).
                where(Users.tg_id == user_tg_id)
            )

            tg_session = await session.execute(query)
            tg_session = tg_session.scalar_one_or_none()

            if tg_session:
                return SessionsPydantic.model_validate(
                    tg_session,
                    from_attributes=True
                )

    @staticmethod
    async def set_session_state(
            state: State,
            user_tg_id: int,
            last_value: str = None,
            account_id: int = None
    ):
        async with async_session_factory() as session:
            user = await session.execute(
                select(Users).where(
                    Users.tg_id == user_tg_id
                )
            )
            user = user.scalar_one_or_none()

            if account_id:
                await session.execute(
                    update(Sessions)
                    .values(
                        account_id=account_id,
                        last_state=state,
                        last_value=last_value
                    )
                    .where(Sessions.user_id == user.id)
                )
            else:
                await session.execute(
                    update(Sessions)
                    .values(
                        last_state=state,
                        last_value=last_value
                    )
                    .where(Sessions.user_id == user.id)
                )
            await session.commit()

    @staticmethod
    async def execute_account(login_account: str) -> AccountsPydantic:
        async with async_session_factory() as session:
            account = await session.execute(
                select(Accounts).where(
                    Accounts.login == login_account
                )
            )
            account = account.scalar_one_or_none()
            if account:
                return AccountsPydantic.model_validate(
                    account,
                    from_attributes=True
                )

    @staticmethod
    async def create_account(login_account: str, user_tg_id: int):
        async with async_session_factory() as session:
            account = Accounts(login=login_account)
            session.add(account)
            await session.commit()

        return account

    @staticmethod
    async def update_account(
            login_account: str,
            name_account: str
    ):
        async with async_session_factory() as session:
            await session.execute(
                update(Accounts)
                .values(
                    name=name_account,
                )
                .where(Accounts.login == login_account)
            )

            await session.commit()

    async def create_task(
            self,
            name: str,
            user_tg_id: int
    ):
        async with async_session_factory() as session:
            tg_state = await self.execute_current_state(user_tg_id)
            task = Tasks(
                account_id=tg_state.account_id,
                name=name,
            )

            session.add(task)
            await session.commit()

    @staticmethod
    async def execute_task(
            user_tg_id,
            task_id: int = None
    ) -> TasksPydantic:
        """
        SELECT t.*
        FROM tasks AS t
        INNER JOIN session AS s
            ON s.account_id = t.account_id
        INNER JOIN users AS u
            ON u.id = s.user_id
        WHERE u.tg_id = $1::int AND s.last_value = t.name
        """
        async with async_session_factory() as session:
            query = (
                select(Tasks).
                select_from(Tasks).
                join(Sessions, Tasks.account_id == Sessions.account_id).
                join(Users, Users.id == Sessions.user_id).
                where(
                    and_(
                        Users.tg_id == user_tg_id,
                        Sessions.last_value == Tasks.name
                        if not task_id
                        else Tasks.id == task_id
                    )
                )
            )

            task = await session.execute(query)
            task = task.scalar_one_or_none()

            if task:
                return TasksPydantic.model_validate(
                    task,
                    from_attributes=True
                )

    @staticmethod
    async def execute_tasks(
            user_tg_id: int
    ) -> list[TasksPydantic]:
        async with async_session_factory() as session:
            query = (
                select(Tasks).
                select_from(Tasks).
                join(Sessions, Tasks.account_id == Sessions.account_id).
                join(Users, Users.id == Sessions.user_id).
                where(Users.tg_id == user_tg_id)
            )

            tasks = await session.execute(query)
            tasks = tasks.scalars().all()
            if tasks:
                return [
                    TasksPydantic.model_validate(
                        task,
                        from_attributes=True
                    )
                    for task in tasks
                ]

    @staticmethod
    async def update_tasks(
            task_id: int,
            description: str
    ):
        async with async_session_factory() as session:
            await session.execute(
                update(Tasks)
                .values(
                    description=description,
                )
                .where(Tasks.id == task_id)
            )

            await session.commit()

    @staticmethod
    async def delete_task(
            task_id: int
    ):
        async with async_session_factory() as session:
            await session.execute(
                delete(Tasks)
                .where(
                    id=task_id,
                )
            )
            await session.commit()

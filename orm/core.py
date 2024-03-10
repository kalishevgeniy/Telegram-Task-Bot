from typing import Optional

from sqlalchemy import select, update, delete, and_

from orm.engine import async_session_factory
from orm.models import Users, Sessions, Accounts, Tasks
from src.enum.last_state import State
from src.pydantic.models import (
    SessionsPydantic,
    AccountsPydantic,
    TasksPydantic
)


class AsyncCore:

    @staticmethod
    async def start(
            user_tg_id: int,
            first_name: str,
            last_name: Optional[str],
    ):
        """
        Create a new user by telegram id, make session and state of session
        :param user_tg_id: Current telegram user id
        :param first_name: First name in telegram
        :param last_name: Last name in telegram
        :return: None
        """
        async with async_session_factory() as session:
            user = await session.execute(
                select(Users).where(
                    Users.tg_id == user_tg_id
                )
            )
            user = user.scalar_one_or_none()
            if not user:
                user = Users(
                    tg_id=user_tg_id,
                    first_name=first_name,
                    last_name=last_name
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
    async def execute_current_state(
            user_tg_id: int
    ) -> SessionsPydantic:
        """
        Execute current state of session. Need for FSM

        SELECT sessions.last_state
        FROM users
        INNER JOIN sessions ON user.id = sessions.user_id
        WHERE user.tg_id = $1::int;

        :param user_tg_id: Current telegram user id
        :return: SessionsPydantic
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
        """
        Update current session state

        :param state: State.Enum
        :param user_tg_id: Current telegram user id
        :param last_value: Value input by user
        :param account_id: Current account login in bot
        :return: None
        """
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
    async def execute_account(
            login_account: str
    ) -> AccountsPydantic:
        """
        Execute account from db

        :param login_account: login account input by user tg
        :return: AccountsPydantic
        """
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
    async def create_account(login_account: str):
        """
        Create new account in db

        :param login_account: account name string
        :return: None
        """
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
        """
        Update account for add name

        :param login_account: login account in db
        :param name_account: create name in current account
        :return: None
        """
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
        """
        Create new task in db

        :param name: task name in db
        :param user_tg_id: current user telegram id
        :return: None
        """
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
        Execute task from db by user telegram id and task id

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
        """
        Execute list tasks by user telegram id

        :param user_tg_id: Current user telegram id
        :return: list[TasksPydantic]
        """
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
            name: str,
            description: str,
            is_complete: bool
    ):
        """
        Update tasks

        :param task_id: current task id
        :param name: new task name
        :param description: new description
        :param is_complete: new state of task
        :return: None
        """
        async with async_session_factory() as session:
            await session.execute(
                update(Tasks)
                .values(
                    name=name,
                    description=description,
                    is_complete=is_complete
                )
                .where(Tasks.id == task_id)
            )

            await session.commit()

    @staticmethod
    async def delete_task(
            task_id: int
    ):
        """
        Delete task from db

        :param task_id: task id
        :return: None
        """
        async with async_session_factory() as session:
            await session.execute(
                delete(Tasks)
                .where(
                    Tasks.id == task_id,
                )
            )
            await session.commit()

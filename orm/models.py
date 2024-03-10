from typing import Optional

from sqlalchemy import (
    ForeignKey,
    Boolean,
    BigInteger
)
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from src.enum.last_state import State


class Base(DeclarativeBase):

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[Optional[str]] = mapped_column()


class Accounts(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Optional[str]] = mapped_column()
    login: Mapped[str] = mapped_column(unique=True)


class Sessions(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=True
    )
    last_state: Mapped[State] = mapped_column()
    last_value: Mapped[Optional[str]] = mapped_column()


class Tasks(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)

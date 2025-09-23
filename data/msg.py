from __future__ import annotations

from typing import Optional

from bafser import IdMixin, Log, SqlAlchemyBase, Undefined
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, Session, mapped_column

import tgapi
from data._tables import Tables
from data.user import User


class Msg(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.Msg

    message_id: Mapped[int]
    message_thread_id: Mapped[Optional[int]]
    chat_id: Mapped[int] = mapped_column(BigInteger)
    text: Mapped[Optional[str]] = mapped_column(String(256))

    @staticmethod
    def new(creator: User, message_id: int, chat_id: int, text: str | None = None, message_thread_id: int | None = None):
        db_sess = Session.object_session(creator)
        assert db_sess
        msg = Msg(message_id=message_id, chat_id=chat_id, text=text, message_thread_id=message_thread_id)

        db_sess.add(msg)
        Log.added(msg, creator, [
            ("message_id", message_id),
            ("chat_id", chat_id),
            ("text", text),
            ("message_thread_id", message_thread_id),
        ])

        return msg

    @staticmethod
    def new_from_data(creator: User, data: tgapi.Message):
        return Msg.new(creator, data.message_id, data.chat.id, data.text, Undefined.default(data.message_thread_id))

    def delete(self, actor: User, commit=True):
        db_sess = Session.object_session(self)
        assert db_sess
        db_sess.delete(self)
        Log.deleted(self, actor, commit=commit)

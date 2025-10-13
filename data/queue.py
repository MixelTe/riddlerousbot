from __future__ import annotations

from typing import Optional, Union

import bafser_tgapi as tgapi
from bafser import IdMixin, Log, SqlAlchemyBase, get_db_session
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data._tables import Tables
from data.msg import Msg
from data.user import User


class Queue(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.Queue

    msg_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.Msg}.id"))
    msg_next_id: Mapped[Optional[int]] = mapped_column(ForeignKey(f"{Tables.Msg}.id"), init=False)
    name: Mapped[str] = mapped_column(String(128))

    msg: Mapped[Msg] = relationship(foreign_keys=[msg_id], init=False)
    msg_next: Mapped[Optional[Msg]] = relationship(foreign_keys=[msg_next_id], init=False)

    @staticmethod
    def new(msg_id: int, name: str):
        queue = Queue(msg_id=msg_id, name=name)
        Log.added(queue)
        return queue

    @staticmethod
    def new_by_message(message: tgapi.Message, name: str):
        msg = Msg.new_from_data2(message)
        return Queue.new(msg.id, name)

    @staticmethod
    def get_by_message(message: tgapi.Message):
        return (get_db_session().query(Queue)
                .join(Msg, (Msg.id == Queue.msg_id) | (Msg.id == Queue.msg_next_id))
                .where(Msg.message_id == message.message_id)
                .first())

    def update_name(self, name: str):
        self.name = name
        Log.updated(self)

    def update_msg(self, message: tgapi.Message):
        new_msg = Msg.new_from_data2(message)
        self.msg.delete2(commit=False)
        self.msg = new_msg
        Log.updated(self)

    def update_msg_next(self, message: Union[tgapi.Message, None]):
        msg_next = None if message is None else Msg.new_from_data2(message)
        if self.msg_next:
            self.msg_next.delete2(commit=False)
        self.msg_next = msg_next
        Log.updated(self)

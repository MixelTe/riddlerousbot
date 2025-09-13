from __future__ import annotations

from typing import Optional, Union

from bafser import IdMixin, Log, SqlAlchemyBase
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

import tgapi
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
    def new(creator: User, msg_id: int, name: str):
        db_sess = Session.object_session(creator)
        assert db_sess
        queue = Queue(msg_id=msg_id, name=name)

        db_sess.add(queue)
        Log.added(queue, creator, [
            ("msg_id", msg_id),
            ("name", name),
        ])

        return queue

    @staticmethod
    def new_by_message(creator: User, message: tgapi.Message, name: str):
        msg = Msg.new_from_data(creator, message)
        return Queue.new(creator, msg.id, name)

    @staticmethod
    def get_by_message(db_sess: Session, message: tgapi.Message):
        return (db_sess.query(Queue)
                .join(Msg, (Msg.id == Queue.msg_id) | (Msg.id == Queue.msg_next_id))
                .where(Msg.message_id == message.message_id)
                .first())

    def update_name(self, actor: User, name: str):
        old_name = self.name
        self.name = name
        Log.updated(self, actor, [("name", old_name, name)])

    def update_msg(self, actor: User, message: tgapi.Message):
        old_msg = self.msg
        self.msg = Msg.new_from_data(actor, message)
        old_msg.delete(actor, commit=False)
        Log.updated(self, actor, [("msg_id", old_msg.id, self.msg.id)])

    def update_msg_next(self, actor: User, message: Union[tgapi.Message, None]):
        old_msg = self.msg_next
        new_msg = None if message is None else Msg.new_from_data(actor, message)
        self.msg_next = new_msg
        if old_msg:
            old_msg.delete(actor, commit=False)
        Log.updated(self, actor, [("msg_next_id", None if old_msg is None else old_msg.id, None if new_msg is None else new_msg.id)])

from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, orm
from sqlalchemy.orm import Session

from bfs import SqlAlchemyBase, IdMixin, Log
from data._tables import Tables
from data.msg import Msg
from data.user import User
import tgapi


class Queue(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.Queue

    msg_id = Column(Integer, ForeignKey("Msg.id"), nullable=False)
    msg_next_id = Column(Integer, ForeignKey("Msg.id"))
    name = Column(String(128), nullable=False)

    msg = orm.relationship("Msg", foreign_keys=[msg_id])
    msg_next = orm.relationship("Msg", foreign_keys=[msg_next_id])

    if TYPE_CHECKING:
        msg: Msg
        msg_next: Msg

    @staticmethod
    def new(creator: User, msg_id: int, name: str):
        db_sess = Session.object_session(creator)
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

    def get_dict(self):
        return self.to_dict(only=("id", "msg_id", "name"))

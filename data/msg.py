from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Session

from bfs import SqlAlchemyBase, IdMixin, Log
from data._tables import Tables
import tgapi


class Msg(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.Msg

    message_id = Column(Integer, nullable=False)
    message_thread_id = Column(Integer, nullable=True)
    chat_id = Column(Integer, nullable=False)
    text = Column(String(256))
    date = Column(DateTime)

    @staticmethod
    def new(db_sess: Session, message_id: int, chat_id: int, message_thread_id: int = None):
        msg = Msg(message_id=message_id, chat_id=chat_id, message_thread_id=message_thread_id)

        db_sess.add(msg)
        Log.added(msg, None, [
            ("message_id", message_id),
            ("chat_id", chat_id),
            ("message_thread_id", message_thread_id),
        ], db_sess=db_sess)

        return msg

    @staticmethod
    def new_from_data(db_sess: Session, data: tgapi.Message):
        return Msg.new(db_sess, data.message_id, data.chat.id, data.message_thread_id)

    def get_dict(self):
        return self.to_dict(only=("id", "message_id", "chat_id", "text", "date"))

from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, orm
from sqlalchemy.orm import Session

from bafser import SqlAlchemyBase, IdMixin, Log
from data._tables import Tables
from data.user import User


class Tagger(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.Tagger

    cmd = Column(String(1024), nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False)

    user = orm.relationship("User", foreign_keys=[user_id], lazy="joined")

    if TYPE_CHECKING:
        user: User

    @staticmethod
    def new(creator: User, cmd: str, chat_id: int, user_id: int, commit=True):
        db_sess = Session.object_session(creator)
        msg = Tagger(cmd=cmd, chat_id=chat_id, user_id=user_id)

        db_sess.add(msg)
        Log.added(msg, creator, [
            ("cmd", cmd),
            ("chat_id", chat_id),
            ("user_id", user_id),
        ], commit=commit)

        return msg

    @staticmethod
    def get_by_value(db_sess: Session, cmd: str, chat_id: int, user_id: int):
        return (db_sess
                .query(Tagger)
                .filter((Tagger.chat_id == chat_id) & (Tagger.cmd == cmd) & (Tagger.user_id == user_id))
                .first())

    @staticmethod
    def get_all_by_cmd_in_chat(db_sess: Session, cmd: str, chat_id: int):
        return db_sess.query(Tagger).filter((Tagger.chat_id == chat_id) & (Tagger.cmd == cmd)).all()

    def delete(self, actor: User):
        db_sess = Session.object_session(actor)
        db_sess.delete(self)
        Log.deleted(self, actor)

    def get_dict(self):
        return self.to_dict(only=("id", "cmd", "chat_id", "user_id"))

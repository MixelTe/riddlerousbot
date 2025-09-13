from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, orm
from sqlalchemy.orm import Session

from bafser import SqlAlchemyBase, IdMixin, Log
from data._tables import Tables
from data.user import User

if TYPE_CHECKING:
    from bot.bot import Bot


class Tagger(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.Tagger

    cmd = Column(String(1024), nullable=False)
    chat_id = Column(BigInteger, nullable=False)
    user_id = Column(Integer, ForeignKey("User.id"), nullable=False)

    user = orm.relationship("User", foreign_keys=[user_id], lazy="joined")

    if TYPE_CHECKING:
        user: User

    @staticmethod
    def update_cmd_in_chat(bot: "Bot", cmd: str, users: list[User]):
        users.sort(key=lambda u: u.name)
        chat_id = bot.chat.id
        Tagger.query_all_by_cmd_in_chat(bot.db_sess, cmd, chat_id).delete()
        user_ids = []
        for user in users:
            user_ids.append(user.id)
            tag = Tagger(cmd=cmd, chat_id=chat_id, user_id=user.id)
            bot.db_sess.add(tag)
        Log.updated(Tagger.FakeForLog(), bot.user, [
            ("cmd", cmd, cmd),
            ("chat_id", chat_id, chat_id),
            ("user_id", [], user_ids),
        ])

    @staticmethod
    def get_by_value(db_sess: Session, cmd: str, chat_id: int, user_id: int):
        return (db_sess
                .query(Tagger)
                .filter((Tagger.chat_id == chat_id) & (Tagger.cmd == cmd) & (Tagger.user_id == user_id))
                .first())

    @staticmethod
    def get_all_by_cmd_in_chat(db_sess: Session, cmd: str, chat_id: int):
        return Tagger.query_all_by_cmd_in_chat(db_sess, cmd, chat_id).all()

    @staticmethod
    def query_all_by_cmd_in_chat(db_sess: Session, cmd: str, chat_id: int):
        return db_sess.query(Tagger).filter((Tagger.chat_id == chat_id) & (Tagger.cmd == cmd))

    def get_dict(self):
        return self.to_dict(only=("id", "cmd", "chat_id", "user_id"))

    class FakeForLog:
        __tablename__ = Tables.Tagger

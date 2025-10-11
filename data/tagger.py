from __future__ import annotations

from typing import TYPE_CHECKING

from bafser import IdMixin, Log, SqlAlchemyBase, get_db_session
from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from data._tables import Tables
from data.user import User

if TYPE_CHECKING:
    from bot.bot import Bot


class Tagger(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.Tagger

    cmd: Mapped[str] = mapped_column(String(1024))
    chat_id: Mapped[int] = mapped_column(BigInteger)
    user_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.User}.id"))

    user: Mapped[User] = relationship(init=False, lazy="joined")

    @staticmethod
    def update_cmd_in_chat(bot: "Bot", cmd: str, users: list[User]):
        users.sort(key=lambda u: u.name)
        assert bot.chat
        chat_id = bot.chat.id
        Tagger.query_all_by_cmd_in_chat(cmd, chat_id).delete()
        user_ids = []
        for user in users:
            user_ids.append(user.id)
            tag = Tagger(cmd=cmd, chat_id=chat_id, user_id=user.id)
            bot.db_sess.add(tag)
        Log.updated(Tagger.FakeForLog(), bot.user, [  # pyright: ignore[reportArgumentType]
            ("cmd", cmd, cmd),
            ("chat_id", chat_id, chat_id),
            ("user_id", [], user_ids),
        ])

    @staticmethod
    def get_by_value(cmd: str, chat_id: int, user_id: int):
        return (get_db_session()
                .query(Tagger)
                .filter((Tagger.chat_id == chat_id) & (Tagger.cmd == cmd) & (Tagger.user_id == user_id))
                .first())

    @staticmethod
    def get_all_by_cmd_in_chat(cmd: str, chat_id: int):
        return Tagger.query_all_by_cmd_in_chat(cmd, chat_id).all()

    @staticmethod
    def query_all_by_cmd_in_chat(cmd: str, chat_id: int):
        return get_db_session().query(Tagger).filter((Tagger.chat_id == chat_id) & (Tagger.cmd == cmd))

    class FakeForLog:
        __tablename__ = Tables.Tagger

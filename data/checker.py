from __future__ import annotations

from bafser import IdMixin, Log, SqlAlchemyBase
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from data._tables import Tables
from data.msg import Msg
from data.user import User


class Checker(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.Checker

    msg_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.Msg}.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.User}.id"))
    cmd: Mapped[str] = mapped_column(String(1024))

    msg: Mapped[Msg] = relationship(init=False, lazy="joined")
    user: Mapped[User] = relationship(init=False)

    @staticmethod
    def new(msg: Msg, user: User, cmd: str, commit: bool = True):
        chk = Checker(msg_id=msg.id, user_id=user.id, cmd=cmd)
        Log.added(chk, commit=commit)
        return chk

    @staticmethod
    def all_by_user(user: User):
        return user.db_sess.query(Checker).filter(Checker.user_id == user.id).all()

    def delete(self, commit=True):
        self.db_sess.delete(self)
        Log.deleted(self, None, [
            ("msg_id", self.msg_id),
            ("user_id", self.user_id),
        ], commit=commit)

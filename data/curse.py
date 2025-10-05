from __future__ import annotations

from datetime import datetime

from bafser import IdMixin, Log, SqlAlchemyBase
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data._tables import Tables
from data.user import User


class Curse(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.Curse

    type: Mapped[str] = mapped_column(String(128))
    user_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.User}.id"))
    end_date: Mapped[datetime]

    user: Mapped[User] = relationship(init=False)

    @staticmethod
    def new(creator: User, user: User, end_date: datetime):
        curse = Curse(type="silence", user_id=user.id, end_date=end_date)

        creator.db_sess.add(curse)
        Log.added(curse, creator, [
            ("type", "silence"),
            ("user_id", user.id),
            ("end_date", end_date.isoformat()),
        ])

        return curse

    @staticmethod
    def get_by_user(user: User):
        return user.db_sess.query(Curse).filter(Curse.user_id == user.id).first()

    def update_end_date(self, actor: User, end_date: datetime):
        old_end_date = self.end_date
        self.end_date = end_date
        Log.updated(self, actor, [
            ("end_date", old_end_date.isoformat(), end_date.isoformat()),
        ])

    def delete(self, actor: User, commit=True):
        db_sess = self.db_sess
        db_sess.delete(self)
        Log.deleted(self, actor, [
            ("type", self.type),
            ("user_id", self.user_id),
            ("end_date", self.end_date.isoformat()),
        ], commit=commit)

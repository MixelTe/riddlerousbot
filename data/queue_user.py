from __future__ import annotations

from datetime import datetime

from bafser import Log, SqlAlchemyBase, get_datetime_now, get_db_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data._tables import Tables
from data.user import User


class QueueUser(SqlAlchemyBase):
    __tablename__ = Tables.QueueUser

    queue_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.Queue}.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.User}.id"), primary_key=True)
    enter_date: Mapped[datetime]

    user: Mapped[User] = relationship(init=False)

    def __repr__(self):
        return f"<QueueUser> qid={self.queue_id} uid={self.user_id}"

    @staticmethod
    def new(queue_id: int, user_id: int, commit=True):
        now = get_datetime_now()
        qu = QueueUser(queue_id=queue_id, user_id=user_id, enter_date=now)
        Log.added(qu, now=now, commit=commit)
        return qu

    @staticmethod
    def get(queue_id: int, user_id: int):
        return get_db_session().query(QueueUser).filter(QueueUser.queue_id == queue_id, QueueUser.user_id == user_id).first()

    @staticmethod
    def get_by_username(queue_id: int, username: str):
        if username.startswith("@"):
            username = username[1:]
        return (get_db_session().query(QueueUser)
                .join(User, User.id == QueueUser.user_id)
                .filter(QueueUser.queue_id == queue_id, User.username == username)
                .first())

    @staticmethod
    def get_by_user_id(queue_id: int, user_id: int):
        return (get_db_session().query(QueueUser)
                .join(User, User.id == QueueUser.user_id)
                .filter(QueueUser.queue_id == queue_id, User.id == user_id)
                .first())

    @staticmethod
    def get_by_order(queue_id: int, order: int):
        return (get_db_session().query(QueueUser)
                .filter(QueueUser.queue_id == queue_id)
                .order_by(QueueUser.enter_date)
                .offset(order)
                .first())

    @staticmethod
    def all_in_queue(queue_id: int):
        return get_db_session().query(QueueUser).filter(QueueUser.queue_id == queue_id).order_by(QueueUser.enter_date).all()

    @staticmethod
    def first2_in_queue(queue_id: int):
        r = get_db_session().query(QueueUser).filter(QueueUser.queue_id == queue_id).order_by(QueueUser.enter_date).limit(2).all()
        if len(r) == 2:
            return r[0], r[1]
        if len(r) == 1:
            return r[0], None
        return None, None

    @staticmethod
    def count_in_queue(queue_id: int):
        return get_db_session().query(QueueUser).filter(QueueUser.queue_id == queue_id).count()

    @staticmethod
    def delete_all_in_queue(queue_id: int):
        db_sess = get_db_session()
        qus = QueueUser.all_in_queue(queue_id)
        for qu in qus:
            qu.delete(commit=False)
        db_sess.commit()

    def delete(self, commit=True):
        self.db_sess.delete(self)
        Log.deleted(self, None, [
            ("queue_id", self.queue_id),
            ("user_id", self.user_id),
        ], commit=commit)

    @staticmethod
    def swap_enter_date(qu1: QueueUser, qu2: QueueUser, commit=True):
        qu1.enter_date, qu2.enter_date = qu2.enter_date, qu1.enter_date
        Log.updated(qu1, commit=False)
        Log.updated(qu2, commit=commit)

    def set_now_as_enter_date(self):
        self.enter_date = get_datetime_now()
        Log.updated(self)

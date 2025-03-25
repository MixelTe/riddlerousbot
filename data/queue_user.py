from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Integer, orm
from sqlalchemy.orm import Session

from bfs import SqlAlchemyBase, Log, get_datetime_now
from data._tables import Tables
from data.user import User


class QueueUser(SqlAlchemyBase):
    __tablename__ = Tables.QueueUser

    queue_id = Column(Integer, ForeignKey("Queue.id"), primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("User.id"), primary_key=True, nullable=False)
    enter_date = Column(DateTime, nullable=False)

    user = orm.relationship("User")

    if TYPE_CHECKING:
        user: User

    @staticmethod
    def new(db_sess: Session, queue_id: int, user_id: int):
        now = get_datetime_now()
        qu = QueueUser(queue_id=queue_id, user_id=user_id, enter_date=now)

        db_sess.add(qu)
        Log.added(qu, None, [
            ("queue_id", queue_id),
            ("user_id", user_id),
            ("date", now.isoformat()),
        ], db_sess=db_sess)

        return qu

    @staticmethod
    def get(db_sess: Session, queue_id: int, user_id: int):
        return db_sess.query(QueueUser).filter(QueueUser.queue_id == queue_id, QueueUser.user_id == user_id).first()

    @staticmethod
    def all_in_queue(db_sess: Session, queue_id: int):
        return db_sess.query(QueueUser).filter(QueueUser.queue_id == queue_id).order_by(QueueUser.enter_date).all()

    @staticmethod
    def delete_all_in_queue(db_sess: Session, queue_id: int):
        db_sess.query(QueueUser).filter(QueueUser.queue_id == queue_id).delete()

    def delete(self):
        db_sess = Session.object_session(self)
        db_sess.delete(self)
        Log.deleted(self, None, db_sess=db_sess)

    def get_dict(self):
        return self.to_dict(only=("queue_id", "user_id", "date"))

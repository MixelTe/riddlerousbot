from __future__ import annotations
from sqlalchemy import DateTime, Column, ForeignKey, Integer
from sqlalchemy import orm
from sqlalchemy.orm import Session
from sqlalchemy_serializer import SerializerMixin

from data.log import Log, Tables
from data.get_datetime_now import get_datetime_now
from data.user import User
from .db_session import SqlAlchemyBase


class UserTask(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "UserTask"

    userId     = Column(Integer, ForeignKey("User.id"), nullable=False)
    taskId     = Column(Integer, ForeignKey("Task.id"), nullable=False)
    date       = Column(DateTime, nullable=False)

    user = orm.relationship("User")
    task = orm.relationship("Task")

    def __repr__(self):
        return f"<UserTask> [{self.id}] {self.userId} - {self.taskId}"

    @staticmethod
    def new(creator: User, userId: int, taskId: int):
        db_sess = Session.object_session(creator)
        now = get_datetime_now()
        userTask = UserTask(userId=userId, taskId=taskId, date=now)

        db_sess.add(userTask)
        Log.added(userTask, creator, Tables.UserTask, [
            ("userId", userId),
            ("taskId", taskId),
        ], now)

        return userTask

    @staticmethod
    def all_by_task(db_sess: Session, taskId: int):
        return db_sess.query(UserTask).filter(UserTask.taskId == taskId).all()

    @staticmethod
    def all_by_user(db_sess: Session, userId: int):
        return db_sess.query(UserTask).filter(UserTask.userId == userId).all()

    def get_dict(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "taskId": self.taskId,
        }

from __future__ import annotations

from sqlalchemy import DateTime, Column, ForeignKey, Integer
from sqlalchemy import orm
from sqlalchemy.orm import Session

from bfs import SqlAlchemyBase, IdMixin, Log, get_datetime_now
from data._tables import Tables
from data.user import User


class UserTask(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.UserTask

    userId = Column(Integer, ForeignKey("User.id"), nullable=False)
    taskId = Column(Integer, ForeignKey("Task.id"), nullable=False)
    date = Column(DateTime, nullable=False)

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
        Log.added(userTask, creator, [
            ("userId", userId),
            ("taskId", taskId),
            ("date", now.isoformat()),
        ], now)

        return userTask

    @staticmethod
    def all_by_task(db_sess: Session, taskId: int):
        return db_sess.query(UserTask).filter(UserTask.taskId == taskId).all()

    @staticmethod
    def all_by_user(db_sess: Session, userId: int):
        return db_sess.query(UserTask).filter(UserTask.userId == userId).all()

    def get_dict(self):
        return self.to_dict(only=("id", "userId", "taskId", "date"))

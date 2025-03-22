from __future__ import annotations
from sqlalchemy import Column, String
from sqlalchemy.orm import Session
from sqlalchemy_serializer import SerializerMixin

from data.log import Log, Tables
from data.user import User
from .db_session import SqlAlchemyBase


class Task(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "Task"

    answer  = Column(String(128), nullable=False)

    def __repr__(self):
        return f"<Task> [{self.id}] {self.answer}"

    @staticmethod
    def new(creator: User, answer: str):
        db_sess = Session.object_session(creator)
        task = Task(answer=answer)

        db_sess.add(task)
        Log.added(task, creator, Tables.Task, [
            ("answer", answer),
        ])

        return task

    def get_dict(self):
        return {
            "id": self.id,
            "answer": self.answer,
        }

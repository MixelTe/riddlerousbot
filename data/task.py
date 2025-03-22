from __future__ import annotations

from sqlalchemy import Column, String
from sqlalchemy.orm import Session

from bfs import SqlAlchemyBase, IdMixin, Log
from data._tables import Tables
from data.user import User


class Task(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.Task

    answer  = Column(String(128), nullable=False)

    def __repr__(self):
        return f"<Task> [{self.id}] {self.answer}"

    @staticmethod
    def new(creator: User, answer: str):
        db_sess = Session.object_session(creator)
        task = Task(answer=answer)

        db_sess.add(task)
        Log.added(task, creator, [
            ("answer", answer),
        ])

        return task

    def get_dict(self):
        return self.to_dict(only=("id", "answer"))

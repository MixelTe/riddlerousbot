from typing import Any
from sqlalchemy import Column, DateTime, ForeignKey, orm, Integer, String, JSON
from sqlalchemy.orm import Session
from sqlalchemy_serializer import SerializerMixin

import data
from data._base import Base
from data.get_datetime_now import get_datetime_now
from .db_session import SqlAlchemyBase


class Log(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "Log"

    id         = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    date       = Column(DateTime, nullable=False)
    actionCode = Column(String(16), nullable=False)
    userId     = Column(Integer, ForeignKey("User.id"), nullable=False)
    userName   = Column(String(64), nullable=False)
    tableName  = Column(String(16), nullable=False)
    recordId   = Column(Integer, nullable=False)
    changes    = Column(JSON, nullable=False)

    user = orm.relationship("User")

    def __repr__(self):
        return f"<Log> [{self.id}] {self.date} {self.actionCode}"

    @staticmethod
    def added(record: Base, creator: "data.User", tableName: str, changes: list[tuple[str, Any]], now: DateTime = None):
        db_sess = Session.object_session(creator)
        if now is None:
            now = get_datetime_now()
        log = Log(
            date=now,
            actionCode=Actions.added,
            userId=creator.id,
            userName=creator.get_name(),
            tableName=tableName,
            recordId=-1,
            changes=list(map(lambda v: (v[0], None, v[1]), changes))
        )
        db_sess.add(log)
        db_sess.commit()
        log.recordId = record.id
        db_sess.commit()
        return log

    def get_dict(self):
        return self.to_dict(only=("id", "date", "actionCode", "userId", "userName", "tableName", "recordId", "changes"))


class Actions:
    added = "added"
    updated = "updated"
    deleted = "deleted"
    restored = "restored"


class Tables:
    User = "User"
    GameMessage = "GameMessage"

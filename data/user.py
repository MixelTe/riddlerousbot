from __future__ import annotations
from sqlalchemy import DefaultClause, Column, Integer, BigInteger, String, Boolean
from sqlalchemy.orm import Session
from sqlalchemy_serializer import SerializerMixin

from data.log import Actions, Log, Tables
from data.get_datetime_now import get_datetime_now
import tgapi
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "User"

    is_admin      = Column(Boolean, DefaultClause("0"), nullable=False)
    id_tg         = Column(BigInteger, index=True, unique=True, nullable=False)
    is_bot        = Column(Boolean, DefaultClause("0"), nullable=False)
    first_name    = Column(String(128), nullable=False)
    last_name     = Column(String(128), nullable=False)
    username      = Column(String(128), nullable=False)
    language_code = Column(String(16), nullable=False)

    def __repr__(self):
        return f"<User> [{self.id} {self.id_tg}] {self.username}"

    def get_name(self):
        if self.username != "":
            return self.username
        return f"${self.id_tg}"

    @staticmethod
    def new(db_sess: Session, id_tg: int, is_bot: bool, first_name: str, last_name: str, username: str, language_code: str, admin = False):
        user = User(id_tg=id_tg, is_bot=is_bot, first_name=first_name, last_name=last_name, username=username, language_code=language_code)

        db_sess.add(user)

        now = get_datetime_now()
        log = Log(
            date=now,
            actionCode=Actions.added,
            userId=1,
            userName="System",
            tableName=Tables.User,
            recordId=-1,
            changes=[
                ("id_tg", None, user.id_tg),
                ("is_bot", None, user.is_bot),
                ("first_name", None, user.first_name),
                ("last_name", None, user.last_name),
                ("username", None, user.username),
                ("language_code", None, user.language_code),
            ]
        )
        if admin:
            user.is_admin = True
        else:
            db_sess.add(log)
        db_sess.commit()

        log.recordId = user.id
        if admin:
            db_sess.add(log)
            log.userId = user.id
        db_sess.commit()

        return user

    @staticmethod
    def new_from_data(db_sess: Session, data: tgapi.User):
        return User.new(db_sess, data.id, data.is_bot, data.first_name, data.last_name, data.username, data.language_code)

    @staticmethod
    def get_by_id_tg(db_sess: Session, id_tg: int):
        return db_sess.query(User).filter(User.id_tg == id_tg).first()

    @staticmethod
    def get_by_username(db_sess: Session, username: str):
        return db_sess.query(User).filter(User.username == username).first()

    @staticmethod
    def get_admin(db_sess: Session):
        return db_sess.query(User).filter(User.is_admin == True).first()

    def get_dict(self):
        return {
            "id": self.id,
            "is_admin": self.is_admin,
            "id_tg": self.id_tg,
            "is_bot": self.is_bot,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "language_code": self.language_code,
        }

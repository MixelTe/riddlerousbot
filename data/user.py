from sqlalchemy import DefaultClause, Column, BigInteger, String, Boolean
from sqlalchemy.orm import Session

from bfs import UserBase, randstr
from data._roles import Roles
import tgapi


class User(UserBase):
    id_tg = Column(BigInteger, index=True, unique=True, nullable=False)
    is_bot = Column(Boolean, DefaultClause("0"), nullable=False)
    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)
    username = Column(String(128), nullable=False)
    language_code = Column(String(16), nullable=False)

    @classmethod
    def new(cls, db_sess: Session, id_tg: int, is_bot: bool, first_name: str, last_name: str, username: str, language_code: str):
        fake_creator = User.get_fake_system()
        return super().new(fake_creator, id_tg, randstr(8), username, [Roles.user], db_sess,
                           id_tg=id_tg, is_bot=is_bot, first_name=first_name, last_name=last_name, username=username, language_code=language_code)

    @staticmethod
    def _new(db_sess: Session, user_kwargs: dict, id_tg: int, is_bot: bool, first_name: str, last_name: str, username: str, language_code: str):
        user = User(**user_kwargs,
                    id_tg=id_tg, is_bot=is_bot, first_name=first_name, last_name=last_name, username=username, language_code=language_code)
        changes = [
            ("id_tg", user.id_tg),
            ("is_bot", user.is_bot),
            ("first_name", user.first_name),
            ("last_name", user.last_name),
            ("username", user.username),
            ("language_code", user.language_code),
        ]
        return user, changes

    @staticmethod
    def create_admin(db_sess: Session):
        return User.new(db_sess, 0, False, "Админ", "", "admin", "en")

    def __repr__(self):
        return f"<User> [{self.id} {self.id_tg}] {self.username}"

    def get_name(self):
        if self.username != "":
            return self.username
        return f"${self.id_tg}"

    def is_admin(self):
        return self.has_role(Roles.admin)

    @staticmethod
    def new_from_data(db_sess: Session, data: tgapi.User):
        return User.new(db_sess, data.id, data.is_bot, data.first_name, data.last_name, data.username, data.language_code)

    @staticmethod
    def get_by_id_tg(db_sess: Session, id_tg: int):
        return User.query(db_sess).filter(User.id_tg == id_tg).first()

    @staticmethod
    def get_by_username(db_sess: Session, username: str):
        return User.query(db_sess).filter(User.username == username).first()

    def get_dict(self):
        return {
            "id": self.id,
            "is_admin": self.has_role(Roles.admin),
            "id_tg": self.id_tg,
            "is_bot": self.is_bot,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "language_code": self.language_code,
        }

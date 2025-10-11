from __future__ import annotations

from bafser import IdMixin, Log, SqlAlchemyBase, get_db_session
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from data._tables import Tables


class Screamer(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.Screamer

    cmd: Mapped[str] = mapped_column(String(1024))
    text: Mapped[str] = mapped_column(String(1024))

    @staticmethod
    def new(cmd: str, text: str):
        msg = Screamer(cmd=cmd, text=text)
        Log.added(msg)
        return msg

    @staticmethod
    def get_by_cmd(cmd: str):
        return get_db_session().query(Screamer).filter(Screamer.cmd == cmd).first()

    def update_text(self, text: str):
        self.text = text
        Log.updated(self)

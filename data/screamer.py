from __future__ import annotations

from bafser import IdMixin, Log, SqlAlchemyBase
from sqlalchemy import String
from sqlalchemy.orm import Mapped, Session, mapped_column

from data._tables import Tables
from data.user import User


class Screamer(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.Screamer

    cmd: Mapped[str] = mapped_column(String(1024))
    text: Mapped[str] = mapped_column(String(1024))

    @staticmethod
    def new(creator: User, cmd: str, text: str):
        db_sess = Session.object_session(creator)
        assert db_sess
        msg = Screamer(cmd=cmd, text=text)

        db_sess.add(msg)
        Log.added(msg, creator, [
            ("cmd", cmd),
            ("text", text),
        ])

        return msg

    @staticmethod
    def get_by_cmd(db_sess: Session, cmd: str):
        return db_sess.query(Screamer).filter(Screamer.cmd == cmd).first()

    def update_text(self, actor: User, text: str):
        old_text = self.text
        self.text = text
        Log.updated(self, actor, [("text", old_text, text)])

from __future__ import annotations

from sqlalchemy import Column, String
from sqlalchemy.orm import Session

from bfs import SqlAlchemyBase, IdMixin, Log
from data._tables import Tables
from data.user import User


class Screamer(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.Screamer

    cmd = Column(String(256))
    text = Column(String(256))

    @staticmethod
    def new(creator: User, cmd: str, text: str):
        db_sess = Session.object_session(creator)
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

    def get_dict(self):
        return self.to_dict(only=("id", "cmd", "text"))

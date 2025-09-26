from __future__ import annotations

from typing import TYPE_CHECKING

import bafser_tgapi as tgapi
from bafser import IdMixin, SqlAlchemyBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

if TYPE_CHECKING:
    from bot.bot import Bot

from data._tables import Tables
from data.user import User

ME = tgapi.MessageEntity


class Transaction(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.Transaction

    from_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.User}.id"))
    to_id: Mapped[int] = mapped_column(ForeignKey(f"{Tables.User}.id"))
    value: Mapped[int]

    user_from: Mapped[User] = relationship(foreign_keys=[from_id], init=False)
    user_to: Mapped[User] = relationship(foreign_keys=[to_id], init=False)

    @staticmethod
    def new(creator: User, user_from: User, user_to: User, value: int):
        db_sess = Session.object_session(creator)
        assert db_sess
        trn = Transaction(from_id=user_from.id, to_id=user_to.id, value=value)

        user_from.coins -= value
        user_to.coins += value
        db_sess.add(trn)
        db_sess.commit()

        return trn

    def notify(self, bot: "Bot", reply_msg_id: int | None = None):
        entities = []
        text = "📝 "
        fname = self.user_from.get_username()
        entities.append(ME.text_mention(ME.len(text), ME.len(fname), self.user_from.id_tg))
        text += fname
        text += "   ->   "
        v = f"{self.value} 🧩"
        entities.append(ME.bold(ME.len(text), ME.len(v)))
        text += v
        text += "   ->   "
        tname = self.user_to.get_username()
        entities.append(ME.text_mention(ME.len(text), ME.len(tname), self.user_from.id_tg))
        text += tname
        reply_parameters = None if reply_msg_id is None else tgapi.ReplyParameters(message_id=reply_msg_id)
        bot.sendMessage(text, entities=entities, reply_parameters=reply_parameters)

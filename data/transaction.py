from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, orm
from sqlalchemy.orm import Session

from bfs import SqlAlchemyBase, IdMixin
if TYPE_CHECKING:
    from bot.bot import Bot
from data._tables import Tables
from data.user import User
import tgapi

ME = tgapi.MessageEntity


class Transaction(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.Transaction

    from_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    to_id = Column(Integer, ForeignKey("User.id"), nullable=True)
    value = Column(Integer, nullable=False)

    user_from = orm.relationship("User", foreign_keys=[from_id])
    user_to = orm.relationship("User", foreign_keys=[to_id])

    if TYPE_CHECKING:
        user_from: User
        user_to: User

    @staticmethod
    def new(creator: User, user_from: User, user_to: User, value: int):
        db_sess = Session.object_session(creator)
        trn = Transaction(user_from=user_from, user_to=user_to, value=value)

        user_from.coins -= value
        user_to.coins += value
        db_sess.add(trn)
        db_sess.commit()

        return trn

    def notify(self, bot: Bot, reply_msg_id: int = None):
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
        reply_parameters = None if reply_msg_id is None else tgapi.ReplyParameters(reply_msg_id)
        bot.sendMessage(text, entities=entities, reply_parameters=reply_parameters)

    def get_dict(self):
        return self.to_dict(only=("id", "from_id", "to_id", "value"))

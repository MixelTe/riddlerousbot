from typing import Optional

from bafser import Undefined
from bafser_tgapi import MsgBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from data._tables import Tables


class Msg(MsgBase):
    __tablename__ = Tables.Msg

    reply_to_id: Mapped[Optional[int]] = mapped_column(ForeignKey(f"{Tables.Msg}.id"), default=None)
    # reply_to: Mapped[Optional["Msg"]] = relationship(init=False, lazy="joined", join_depth=2)

    @classmethod
    def get_by_message_id(cls, db_sess: Session, message_id: int):
        return cls.query(db_sess).filter(cls.message_id == message_id).first()

    @classmethod
    def new_from_data(cls, creator, data, reply_to_id: "int | None" = None):
        m = cls.new(creator, data.message_id, data.chat.id, data.text, Undefined.default(data.message_thread_id))
        m.reply_to_id = reply_to_id
        creator.db_sess.commit()
        return m

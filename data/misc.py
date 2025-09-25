from __future__ import annotations

from typing import Optional

from bafser import SingletonMixin, SqlAlchemyBase
from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from data._tables import Tables


class Misc(SqlAlchemyBase, SingletonMixin):
    __tablename__ = Tables.Misc

    os418_chat_id: Mapped[int] = mapped_column(BigInteger)
    os418_chat_thread_id: Mapped[Optional[int]]

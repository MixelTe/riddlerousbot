from __future__ import annotations

import tgapi
from data._tables import Tables


class Msg(tgapi.MsgBase):
    __tablename__ = Tables.Msg

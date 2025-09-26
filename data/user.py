from bafser_tgapi import TgUserBase
from sqlalchemy.orm import Mapped, mapped_column

from data._roles import Roles


class User(TgUserBase):
    _default_role = Roles.user

    is_friendly: Mapped[bool] = mapped_column(server_default="0", init=False)
    coins: Mapped[int] = mapped_column(server_default="100", init=False)

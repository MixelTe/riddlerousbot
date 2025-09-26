from sqlalchemy.orm import Mapped, mapped_column

import tgapi
from data._roles import Roles


class User(tgapi.TgUserBase):
    _default_role = Roles.user

    is_friendly: Mapped[bool] = mapped_column(server_default="0", init=False)
    coins: Mapped[int] = mapped_column(server_default="100", init=False)

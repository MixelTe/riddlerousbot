from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

from bafser import IdMixin, SqlAlchemyBase, get_datetime_now, get_db_session
from sqlalchemy import Text
from sqlalchemy.orm import Mapped, Session, mapped_column

from data._tables import Tables
from utils import parse_int


class Cache(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.Cache

    value: Mapped[str] = mapped_column(Text)
    fresh_until: Mapped[datetime] = mapped_column(index=True)

    @staticmethod
    def put[T](value: T, value_type: type[T], *, db_sess: Session | None = None, commit: bool = True) -> int:
        cache = Cache(
            value=json.dumps({"type": repr(value_type), "value": value}),
            fresh_until=get_datetime_now() + timedelta(hours=1),
        )

        if db_sess is None:
            db_sess = get_db_session()

        db_sess.add(cache)

        if commit:
            db_sess.commit()
        else:
            db_sess.flush()

        return cache.id

    @staticmethod
    def pop[T](id: int | str | None, expected_type: type[T], *, commit: bool = True) -> T | None:
        id = parse_int(id) if isinstance(id, str) else id
        if not id:
            return None

        cache = Cache.get2(id)
        if not cache:
            return None

        data: dict[str, Any] = json.loads(cache.value)

        if data.get("type") != repr(expected_type):
            return None

        cache.db_sess.delete(cache)
        if commit:
            cache.db_sess.commit()
        return data.get("value")

    @staticmethod
    def delete_stale():
        db_sess = get_db_session()
        db_sess.query(Cache).filter(Cache.fresh_until < get_datetime_now()).delete()
        db_sess.commit()

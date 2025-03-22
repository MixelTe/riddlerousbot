import sqlalchemy as sa
from sqlalchemy.orm import Session


class Base:
    id = sa.Column(sa.Integer, primary_key=True, unique=True, autoincrement=True)

    @classmethod
    def get(cls, db_sess: Session, id: int):
        return db_sess.get(cls, id)

    @classmethod
    def all(cls, db_sess: Session):
        return db_sess.query(cls).all()

    def get_dict(self):
        return {
            "id": self.id,
        }

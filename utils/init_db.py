from bafser import AppConfig
from sqlalchemy.orm import Session

from data.user import Roles, User


def init_db(db_sess: Session, config: AppConfig):
    u = User.new(5377785956, False, "Mixel", "", "MixelTe", "en", db_sess=db_sess)
    u.add_role(u, Roles.admin)

    db_sess.commit()

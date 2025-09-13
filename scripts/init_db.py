from bafser import AppConfig
from sqlalchemy.orm import Session

from data.user import Roles, User


def init_db(db_sess: Session, config: AppConfig):
    u = User.new(db_sess, 5377785956, False, "Mixel", "", "MixelTe", "en")
    u.add_role(u, Roles.admin)

    db_sess.commit()

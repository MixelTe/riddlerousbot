from sqlalchemy.orm import Session

from bfs import db_session
from data.user import User
import tgapi

class Bot(tgapi.Bot):
    db_sess: Session = None
    user: User = None

    def before_process_update(self, tguser: tgapi.User):
        db_sess = db_session.create_session()
        user = User.get_by_id_tg(db_sess, tguser.id)
        if user is None:
            user = User.new_from_data(db_sess, tguser)
        self.db_sess = db_sess
        self.user = user

    def after_process_update(self):
        self.db_sess.close()

import bot.queue.base
import bot.queue.manage

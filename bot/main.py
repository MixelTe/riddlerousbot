from sqlalchemy.orm import Session

from bfs import use_db_session
from bot.bot import Bot
from bot.bot_admin import BotAdmin
from data.user import User
import tgapi

bot_admin = BotAdmin()
bot = Bot()


class BotMaster(tgapi.Bot):
    def on_message(self):
        bot_redirect(self.message.sender)

    def on_callback_query(self):
        bot_redirect(self.callback_query.sender)

    def on_inline_query(self):
        bot_redirect(self.inline_query.sender)

    def on_chosen_inline_result(self):
        bot_redirect(self.chosen_inline_result.sender)


bot_master = BotMaster()


def process_update(update: tgapi.Update):
    print(update)
    bot_master.process_update(update)


@use_db_session()
def bot_redirect(tguser: tgapi.User, db_sess: Session):
    user = User.get_by_id_tg(db_sess, tguser.id)
    if user is None:
        user = User.new_from_data(db_sess, tguser)
    b = bot_admin if user.is_admin() else bot
    b.db_sess = db_sess
    b.user = user
    b.process_update(bot_master.update)

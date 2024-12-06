from sqlalchemy.orm import Session

from data.user import User
import tgapi
from utils import use_db_session

def process_update(update: tgapi.Update):
    print(update)
    if update.message and update.message.text != "":
        onMessage(update.message)


@use_db_session()
def onMessage(message: tgapi.Message, db_sess: Session):
    user = User.get_by_id_tg(db_sess, message.sender.id)
    if user is None:
        user = User.new_from_data(db_sess, message.sender)
    if user.is_admin:
        text = f"Hi! {user.first_name}\nDo you say: {message.text}?"
    else:
        text = "Мне не разрешают разговаривать с незнакомцами("
    tgapi.sendMessage(message.chat.id, text)


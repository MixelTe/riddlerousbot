from sqlalchemy.orm import Session

import tgapi


class Bot(tgapi.Bot):
    db_sess: Session = None
    user: tgapi.User = None

    def on_message(self):
        text = "Мне не разрешают разговаривать с незнакомцами("
        self.sendMessage(text)

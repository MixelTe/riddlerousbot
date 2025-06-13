from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, orm
from sqlalchemy.orm import Session

from bafser import SqlAlchemyBase, IdMixin, Log
from data._tables import Tables
from data.msg import Msg
from data.user import User
import tgapi


class TicTacToe(SqlAlchemyBase, IdMixin):
    __tablename__ = Tables.TicTacToe

    msg_id = Column(Integer, ForeignKey("Msg.id"), nullable=False)
    player1_id = Column(Integer, ForeignKey("User.id"), nullable=False)
    player2_id = Column(Integer, ForeignKey("User.id"), nullable=True)
    field = Column(String(10), nullable=False)

    msg = orm.relationship("Msg", foreign_keys=[msg_id])
    player1 = orm.relationship("User", foreign_keys=[player1_id])
    player2 = orm.relationship("User", foreign_keys=[player2_id])

    if TYPE_CHECKING:
        msg: Msg
        player1: User
        player2: User

    @staticmethod
    def new(creator: User, msg_id: int, player1_id: int, player2_id: int = None):
        db_sess = Session.object_session(creator)
        field = "0" * 9
        game = TicTacToe(msg_id=msg_id, player1_id=player1_id, player2_id=player2_id, field=field)

        db_sess.add(game)
        Log.added(game, creator, [
            ("msg_id", msg_id),
            ("player1_id", player1_id),
            ("player2_id", player2_id),
        ])

        return game

    @staticmethod
    def new_by_message(creator: User, message: tgapi.Message, player1_id: int, player2_id: int = None):
        msg = Msg.new_from_data(creator, message)
        return TicTacToe.new(creator, msg.id, player1_id, player2_id)

    @staticmethod
    def get_by_message(db_sess: Session, message: tgapi.Message):
        return (db_sess.query(TicTacToe)
                .join(Msg, Msg.id == TicTacToe.msg_id)
                .where(Msg.message_id == message.message_id)
                .first())

    def update_player2(self, actor: User, player2_id: int):
        old_player2_id = self.player2_id
        self.player2_id = player2_id
        Log.updated(self, actor, [("player2_id", old_player2_id, player2_id)])

    def get_status(self):
        winner: int = None

        def set_winner(row):
            nonlocal winner
            if row == "111":
                winner = 1
            elif row == "222":
                winner = 2

        for y in range(3):
            set_winner(self.field[y * 3:y * 3 + 3])
        for y in range(3):
            set_winner(self.field[y] + self.field[y + 3] + self.field[y + 6])
        set_winner(self.field[0] + self.field[4] + self.field[8])
        set_winner(self.field[2] + self.field[4] + self.field[6])

        if winner:
            return "winner", winner

        c0 = str(self.field).count("0")
        c1 = str(self.field).count("1")
        c2 = str(self.field).count("2")
        if c0 == 0:
            return "draw", 0
        turn = 1 if c2 > c1 else 2
        return "turn", turn

    def get_dict(self):
        return self.to_dict(only=("id", "msg_id", "player1_id", "player2_id"))

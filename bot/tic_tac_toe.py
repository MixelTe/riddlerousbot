import math

import bafser_tgapi as tgapi

from bot.bot import Bot
from data.tic_tac_toe import TicTacToe
from data.transaction import Transaction
from data.user import User
from utils import parse_int

GAME_WIN_VALUE = 5


@Bot.add_command(desc=("Крестики нолики", "[oppenent]"))
def tic_tac_toe(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    msgb = tgapi.build_msg().bold("👾 Крестики-нолики\n")
    uname = bot.user.get_username()
    msgb.text_mention(uname, bot.user.id_tg)
    msgb.text(" вызывает на дуэль ")
    opponent = None
    if len(args) == 0:
        msgb.text("первого встречного!")
    else:
        opponent = User.get_by_username(bot.db_sess, args[0])
        if not opponent:
            return f"👻 Этот пользователь ({args[0]}) не знаком боту (если в имени ошибки нет, пускай он хотя бы раз повзаимодействует с ботом)"
        oname = opponent.get_username()
        msgb.text_mention(oname, opponent.id_tg).text("!")

    ok, msg = bot.sendMessage(msgb)
    if not ok:
        return "Error!"
    game = TicTacToe.new_by_message(bot.user, msg, bot.user.id, opponent.id if opponent else None)
    bot.logger.info(f"created {game.id} by uid={bot.user.id} ({bot.user.get_username()})")

    tgapi.editMessageReplyMarkup(msg.chat.id, msg.message_id, reply_markup=tgapi.reply_markup([
        ("⚔ Принять вызов!", f"tic_tac_toe_join {game.id}"),
    ]))


@Bot.add_command()
def tic_tac_toe_join(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    game = get_game(bot, args)
    if game.player2_id != None:
        if bot.user.id != game.player2_id:
            return "Вызвали на дуэль не вас!"

    game.update_player2(bot.user, bot.user.id)
    bot.logger.info(f"joined {game.id} by uid={bot.user.id} ({bot.user.get_username()})")

    update_msg(game)


@Bot.add_command()
def tic_tac_toe_turn(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    game = get_game(bot, args)
    if len(args) < 3:
        return "No coords provided"
    x = parse_int(args[1])
    if x is None or x < 0 or x >= 3:
        return "x is NaN"
    y = parse_int(args[2])
    if y is None or y < 0 or y >= 3:
        return "y is NaN"

    if game.player2 == None:
        return "Игра ещё не началась"

    i = y * 3 + x
    if game.field[i] != "0":
        return "Клетка уже занята"

    status, player_i = game.get_status()
    if status != "turn":
        return "Игра уже окончена"
    player = game.player1 if player_i == 1 else game.player2

    if player.id != bot.user.id:
        return "Сейчас не ваш ход"

    game.field = game.field[:i] + str(player_i) + game.field[i + 1:]
    bot.db_sess.commit()
    bot.logger.info(f"turn {game.id} at ({x};{y}) by uid={bot.user.id} ({bot.user.get_username()})")

    status, player_i = game.get_status()
    if status == "winner":
        winner = game.player1 if player_i == 1 else game.player2
        looser = game.player2 if player_i == 1 else game.player1
        if looser.coins >= GAME_WIN_VALUE:
            trn = Transaction.new(bot.user, user_from=looser, user_to=winner, value=GAME_WIN_VALUE)
            trn.notify(bot, game.msg.message_id)
        bot.logger.info(f"win {game.id} by uid={player.id} ({player.get_username()})")
    elif status == "draw":
        bot.logger.info(f"draw {game.id} by uid={player.id} ({player.get_username()})")

    update_msg(game)


def get_game(bot: Bot, args: tgapi.BotCmdArgs):
    if len(args) < 1:
        tgapi.raiseBotAnswer("No game id provided")

    id = parse_int(args[0])
    if id is None:
        tgapi.raiseBotAnswer("id is NaN")

    game = TicTacToe.get(bot.db_sess, id, for_update=True)
    if game is None:
        tgapi.raiseBotAnswer(f"game with id={id} doesnt exist")

    return game


def update_msg(game: TicTacToe):
    assert game.player2
    player1_piece = get_player_piece(game.player1.id_tg, True)
    player2_piece = get_player_piece(game.player2.id_tg, False)
    msg = tgapi.build_msg().bold("👾 Крестики-нолики\n")
    msg.text_mention(player1_piece + " " + game.player1.get_username(), game.player1.id_tg)
    msg.text(" против ")
    msg.text_mention(player2_piece + " " + game.player2.get_username(), game.player2.id_tg)
    msg.text("\n")

    status, player_i = game.get_status()
    player = game.player1 if player_i == 1 else game.player2
    player_piece = player1_piece if player_i == 1 else player2_piece
    pname = player_piece + " " + player.get_username()
    if status == "turn":
        msg.text("⚔ Ходит ")
        msg.text_mention(pname, player.id_tg)
    elif status == "draw":
        msg.text("🥳 Ничья!")
    else:
        msg.text("🥳 Победа за ")
        msg.text_mention(pname, player.id_tg)
        msg.text("!")

    btns: list[list[tuple[str, str]]] = [[] for _ in range(3)]
    for i, ch in enumerate(game.field):
        x = i % 3
        y = i // 3
        txt = "〰"
        if ch == "1":
            txt = player1_piece
        elif ch == "2":
            txt = player2_piece
        elif status == "turn":
            if player_i == 1:
                txt = "⏹"
            else:
                txt = "⏺"
        btns[y].append((txt, f"tic_tac_toe_turn {game.id} {x} {y}"))

    text, entities = msg.build()
    tgapi.editMessageText(game.msg.chat_id, game.msg.message_id, text,
                          reply_markup=tgapi.reply_markup(*btns), entities=entities)


def get_player_piece(id: int, cross: bool):
    # return "⭕❌"[cross]
    piece1 = "🔴🟠🟡🟢🔵🟣🟤⚫⚪"
    piece2 = "🟥🟧🟨🟩🟦🟪🟫⬛⬜"
    a = 7320519545
    b = (1 << 16) - 1
    c = 37320
    i = math.floor((((id * a) & b) ^ c) / (b + 1) * len(piece1))
    if cross:
        return piece2[i]
    return piece1[i]

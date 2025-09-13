import tgapi
from bot.bot import Bot
from data.user import User


def get_users_from_msg(bot: Bot, args: tgapi.BotCmdArgs):
    assert bot.db_sess
    assert bot.message
    usernames: list[str] = []
    users: list[User] = []
    users_not_found: list[str] = []

    users_notag = [e for e in bot.message.entities if e.type == "text_mention"]
    for e in users_notag:
        username = e.get_msg_text(args.input)
        if username in usernames:
            continue
        usernames.append(username)
        assert e.user
        user = User.get_by_id_tg(bot.db_sess, e.user.id)
        if user:
            users.append(user)
        else:
            users_not_found.append(username)

    for username in args:
        if username in usernames:
            continue
        usernames.append(username)
        user = User.get_by_username(bot.db_sess, username)
        if user:
            users.append(user)
        else:
            users_not_found.append(username)

    err = None
    if len(users_not_found) != 0:
        if len(users_not_found) == 1:
            err = f"👻 Этот пользователь не знаком боту: {users_not_found[0]}" + \
                "\n(если в имени ошибки нет, пускай он хотя бы раз повзаимодействует с ботом)"
        err = f"Эти пользователи не знакомы боту: {', '.join(users_not_found)}" + \
            "\n(если в именах ошибки нет, пускай они хотя бы раз повзаимодействуют с ботом)"

    return users, err


def silent_mode(bot: Bot, args: tgapi.BotCmdArgs):
    if len(args) == 0 or args[-1] != "\\s":
        return False
    args.args = args.args[:-1]
    if bot.message:
        tgapi.deleteMessage(bot.message.chat.id, bot.message.message_id)
    return True


def silent_mode_on(bot: Bot):
    if bot.message:
        tgapi.deleteMessage(bot.message.chat.id, bot.message.message_id)


def check_is_member_of_chat(bot: Bot, user: User):
    if bot.chat is None:
        return False

    ok, r = tgapi.getChatMember(bot.chat.id, user.id_tg)
    if not ok:
        return False

    return r.status != "left" and r.status != "kicked"

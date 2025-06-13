from bot.bot import Bot
from data.user import User
import tgapi


def get_users_by_tags(bot: Bot, tags: tgapi.BotCmdArgs):
    users: list[User] = []
    users_not_found: list[str] = []
    for username in tags:
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

import sys
import os


def init_values(dev=False, cmd=False):
    if dev:
        if not os.path.exists("db"):
            os.makedirs("db")
        if cmd:
            add_parent_to_path()
    else:
        add_parent_to_path()

    from data import db_session
    from data.get_datetime_now import get_datetime_now
    from data.log import Log, Actions, Tables
    from data.user import User

    now = get_datetime_now()

    def log(db_sess, user_admin, tableName, recordId, changes):
        db_sess.add(Log(
            date=now,
            actionCode=Actions.added,
            userId=user_admin.id,
            userName=user_admin.name,
            tableName=tableName,
            recordId=recordId,
            changes=changes
        ))

    def init():
        db_session.global_init(dev)
        db_sess = db_session.create_session()

        user_admin = User.new(db_sess, 5377785956, False, "Mixel", "", "MixelTe", "en", admin=True)
        db_sess.commit()

        if dev:
            init_values_dev(db_sess, user_admin)

    def init_values_dev(db_sess, user_admin):
        pass
        # from datetime import timedelta
        # from random import randint, choice
        # import shutil
        # from utils.randstr import randstr

        # db_sess.commit()

    init()


def add_parent_to_path():
    current = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(current)
    sys.path.append(parent)


def read_file(path):
    with open(path) as f:
        return f.read()


if __name__ == "__main__":
    init_values("dev" in sys.argv, True)
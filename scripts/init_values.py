import sys
import os


def init_values(dev=False, cmd=False):
    print(f"init_values {dev=}")
    if cmd:
        add_parent_to_path()

    from bfs import db_session, init_db_values
    from data._roles import Roles
    from data.user import User

    if cmd or not dev:
        init_db_values(dev)

    db_session.global_init(dev)
    db_sess = db_session.create_session()

    u = User.new(db_sess, 5377785956, False, "Mixel", "", "MixelTe", "en")
    u.add_role(u, Roles.admin)

    db_sess.commit()
    db_sess.close()


def add_parent_to_path():
    current = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(current)
    sys.path.append(parent)


if __name__ == "__main__":
    init_values("dev" in sys.argv, True)

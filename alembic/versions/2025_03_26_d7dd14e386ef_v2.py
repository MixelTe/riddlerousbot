"""v2

Revision ID: d7dd14e386ef
Revises: a7bff8adb161
Create Date: 2025-03-26 23:10:26.011710

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd7dd14e386ef'
down_revision: Union[str, None] = 'a7bff8adb161'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Msg', schema=None) as batch_op:
        batch_op.alter_column('chat_id',
               existing_type=sa.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False)

    with op.batch_alter_table('User', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_friendly', sa.Boolean(), server_default='0', nullable=False))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('User', schema=None) as batch_op:
        batch_op.drop_column('is_friendly')

    with op.batch_alter_table('Msg', schema=None) as batch_op:
        batch_op.alter_column('chat_id',
               existing_type=sa.BigInteger(),
               type_=sa.INTEGER(),
               existing_nullable=False)

    # ### end Alembic commands ###

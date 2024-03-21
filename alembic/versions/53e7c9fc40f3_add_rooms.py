"""Add rooms

Revision ID: 53e7c9fc40f3
Revises: c5e62fdfbe90
Create Date: 2024-03-17 16:37:10.181984

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53e7c9fc40f3'
down_revision: Union[str, None] = 'c5e62fdfbe90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('rooms', sa.Column('guest_id', sa.Integer(), nullable=True))
    op.drop_index('ix_rooms_status', table_name='rooms')
    op.drop_index('ix_rooms_title', table_name='rooms')
    op.create_foreign_key(None, 'rooms', 'users', ['guest_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'rooms', type_='foreignkey')
    op.create_index('ix_rooms_title', 'rooms', ['title'], unique=False)
    op.create_index('ix_rooms_status', 'rooms', ['status'], unique=False)
    op.drop_column('rooms', 'guest_id')
    # ### end Alembic commands ###

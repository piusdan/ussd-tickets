"""empty message

Revision ID: a654e00718f8
Revises: dae21d5a6aa8
Create Date: 2017-08-23 13:32:43.033080

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a654e00718f8'
down_revision = 'dae21d5a6aa8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('purchases', sa.Column('confirmed', sa.Boolean(), nullable=True))
    op.drop_index('ix_users_email', table_name='users')
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.create_index('ix_users_email', 'users', ['email'], unique=1)
    op.drop_column('purchases', 'confirmed')
    # ### end Alembic commands ###
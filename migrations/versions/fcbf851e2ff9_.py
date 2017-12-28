"""empty message

Revision ID: fcbf851e2ff9
Revises: c6894ebbdcea
Create Date: 2017-12-28 23:22:49.504794

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fcbf851e2ff9'
down_revision = 'c6894ebbdcea'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.create_index(op.f('ix_subscribers_phoneNumber'), 'subscribers', ['phoneNumber'], unique=False)
    # op.drop_index('ix_subscribers_phoneNumber', table_name='subscribers')
    # ### end Alembic commands ###
    pass


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_subscribers_phoneNumber', 'subscribers', ['phoneNumber'], unique=False)
    op.drop_index(op.f('ix_subscribers_phoneNumber'), table_name='subscribers')
    # ### end Alembic commands ###

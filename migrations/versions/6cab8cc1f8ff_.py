"""empty message

Revision ID: 6cab8cc1f8ff
Revises: 611fc3f13b14
Create Date: 2017-12-28 07:44:09.805302

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6cab8cc1f8ff'
down_revision = '611fc3f13b14'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('messages', sa.Column('last_broadcast', sa.DateTime(), nullable=True))
    op.add_column('subscriptions', sa.Column('at_messageId', sa.Integer(), nullable=True))
    op.add_column('subscriptions', sa.Column('status', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('subscriptions', 'status')
    op.drop_column('subscriptions', 'at_messageId')
    op.drop_column('messages', 'last_broadcast')
    # ### end Alembic commands ###
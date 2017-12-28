"""empty message

Revision ID: b255d3002924
Revises: 
Create Date: 2017-12-29 00:50:03.854064

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b255d3002924'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('campaigns',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=32), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('expiry', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_campaigns_id'), 'campaigns', ['id'], unique=False)
    op.create_index(op.f('ix_campaigns_timestamp'), 'campaigns', ['timestamp'], unique=False)
    op.create_index(op.f('ix_campaigns_title'), 'campaigns', ['title'], unique=True)
    op.create_table('codes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('country', sa.String(length=12), nullable=False),
    sa.Column('currency_code', sa.String(length=4), nullable=False),
    sa.Column('country_code', sa.String(length=4), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('country')
    )
    op.create_table('intervals',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=True),
    sa.Column('seconds', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_intervals_name'), 'intervals', ['name'], unique=True)
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('default', sa.Boolean(), nullable=True),
    sa.Column('permissions', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_roles_default'), 'roles', ['default'], unique=False)
    op.create_table('type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('default', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('address',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('city', sa.String(length=64), nullable=True),
    sa.Column('location', sa.String(length=12), nullable=True),
    sa.Column('code_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['code_id'], ['codes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('choices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('keyword', sa.String(length=16), nullable=False),
    sa.Column('campaign_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_choices_id'), 'choices', ['id'], unique=False)
    op.create_index(op.f('ix_choices_name'), 'choices', ['name'], unique=False)
    op.create_table('messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('expiry', sa.DateTime(), nullable=True),
    sa.Column('last_broadcast', sa.DateTime(), nullable=True),
    sa.Column('slug', sa.String(), nullable=True),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('interval_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['interval_id'], ['intervals.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('broadcasts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('day', sa.DateTime(), nullable=True),
    sa.Column('failed_count', sa.Integer(), nullable=True),
    sa.Column('sucess_count', sa.Integer(), nullable=True),
    sa.Column('sent_count', sa.Integer(), nullable=True),
    sa.Column('message_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('address_id', sa.Integer(), nullable=True),
    sa.Column('slug', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['address_id'], ['address.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_event_name'), 'event', ['name'], unique=True)
    op.create_table('subscribers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone_number', sa.String(length=14), nullable=False),
    sa.Column('attempts', sa.Integer(), nullable=True),
    sa.Column('choice_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['choice_id'], ['choices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscribers_id'), 'subscribers', ['id'], unique=False)
    op.create_index(op.f('ix_subscribers_phone_number'), 'subscribers', ['phone_number'], unique=False)
    op.create_table('subscriptions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone_number', sa.String(), nullable=False),
    sa.Column('message_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('at_messageId', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscriptions_phone_number'), 'subscriptions', ['phone_number'], unique=False)
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('phone_number', sa.String(length=64), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('avatar_hash', sa.String(length=32), nullable=True),
    sa.Column('member_since', sa.DateTime(), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('_password', sa.String(length=128), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('address_id', sa.Integer(), nullable=True),
    sa.Column('slug', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['address_id'], ['address.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_phone_number'), 'user', ['phone_number'], unique=True)
    op.create_table('accounts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('balance', sa.Float(), nullable=True),
    sa.Column('points', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('packages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('remaining', sa.Integer(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.Column('type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.ForeignKeyConstraint(['type_id'], ['type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transactions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=12), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('request_id', sa.String(length=255), nullable=True),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('transaction_cost', sa.Float(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tickets',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('number', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('code', sa.String(length=64), nullable=True),
    sa.Column('package_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['package_id'], ['packages.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tickets')
    op.drop_table('transactions')
    op.drop_table('packages')
    op.drop_table('accounts')
    op.drop_index(op.f('ix_user_phone_number'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_subscriptions_phone_number'), table_name='subscriptions')
    op.drop_table('subscriptions')
    op.drop_index(op.f('ix_subscribers_phone_number'), table_name='subscribers')
    op.drop_index(op.f('ix_subscribers_id'), table_name='subscribers')
    op.drop_table('subscribers')
    op.drop_index(op.f('ix_event_name'), table_name='event')
    op.drop_table('event')
    op.drop_table('broadcasts')
    op.drop_table('messages')
    op.drop_index(op.f('ix_choices_name'), table_name='choices')
    op.drop_index(op.f('ix_choices_id'), table_name='choices')
    op.drop_table('choices')
    op.drop_table('address')
    op.drop_table('type')
    op.drop_index(op.f('ix_roles_default'), table_name='roles')
    op.drop_table('roles')
    op.drop_index(op.f('ix_intervals_name'), table_name='intervals')
    op.drop_table('intervals')
    op.drop_table('codes')
    op.drop_index(op.f('ix_campaigns_title'), table_name='campaigns')
    op.drop_index(op.f('ix_campaigns_timestamp'), table_name='campaigns')
    op.drop_index(op.f('ix_campaigns_id'), table_name='campaigns')
    op.drop_table('campaigns')
    # ### end Alembic commands ###

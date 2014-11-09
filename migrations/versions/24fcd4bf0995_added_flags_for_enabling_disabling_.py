"""Added flags for enabling/disabling whitelist/blacklist

Revision ID: 24fcd4bf0995
Revises: 72759e12019
Create Date: 2014-11-08 23:55:53.902362

"""

# revision identifiers, used by Alembic.
revision = '24fcd4bf0995'
down_revision = '72759e12019'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('users', sa.Column('enable_blacklist', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('enable_whitelist', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('users', 'enable_whitelist')
    op.drop_column('users', 'enable_blacklist')


"""Initial migration - create message table

Revision ID: 4a2253497ee2
Revises: 
Create Date: 2023-03-15 18:38:42.615235

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a2253497ee2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'message',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_message'))
    )


def downgrade():
    op.drop_table('message')

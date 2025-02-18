"""Initial revision - create user and message tables

Revision ID: 87c19c733da2
Revises: 
Create Date: 2024-05-05 21:07:58.861840

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87c19c733da2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'message',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_message'))
    )
    op.create_table(
        'user',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_user')),
        sa.UniqueConstraint('name', name=op.f('uq_user_name'))
    )


def downgrade():
    op.drop_table('user')
    op.drop_table('message')

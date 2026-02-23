"""Initial migration - create user table

Revision ID: 4522be0c4858
Revises:
Create Date: 2025-04-09 19:36:33.944119

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '4522be0c4858'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column(
            'creation_date',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=False),
        sa.Column('last_name', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=True),
        sa.Column(
            'role',
            sa.Enum('ADMINISTRATOR', 'USER', name='role'),
            nullable=False,
        ),
        sa.Column(
            'enabled',
            sa.Boolean(),
            server_default=sa.text('TRUE'),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_user')),
        sa.UniqueConstraint('email', name=op.f('uq_user_email'))
    )


def downgrade() -> None:
    op.drop_table('user')
    op.execute('DROP TYPE role')

"""Create (demo) message table

Revision ID: 01d29545f949
Revises: 4522be0c4858
Create Date: 2025-04-09 19:42:26.174893

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01d29545f949'
down_revision = '4522be0c4858'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'message',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column(
            'date',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column('author_id', sa.Uuid(), nullable=True),
        sa.Column('text', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ['author_id'],
            ['user.id'],
            name=op.f('fk_message_author_id_user'),
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_message'))
    )


def downgrade() -> None:
    op.drop_table('message')

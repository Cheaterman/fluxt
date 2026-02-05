"""Create file table

Revision ID: 43489581b73d
Revises: 01d29545f949
Create Date: 2026-02-03 17:43:45.909208

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '43489581b73d'
down_revision = '4522be0c4858'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'file',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column(
            'creation_date',
            sa.DateTime(),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column('author_id', sa.Uuid(), nullable=True),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ['author_id'],
            ['user.id'],
            name=op.f('fk_file_author_id_user'),
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_file'))
    )

    with op.batch_alter_table('file', schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f('ix_file_filename'),
            ['filename'],
            unique=True,
        )


def downgrade() -> None:
    with op.batch_alter_table('file', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_file_filename'))

    op.drop_table('file')

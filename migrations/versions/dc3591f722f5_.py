"""empty message

Revision ID: dc3591f722f5
Revises: 1a19d4d964e7
Create Date: 2023-10-19 21:30:08.216507

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dc3591f722f5'
down_revision = '1a19d4d964e7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('annotation_task', schema=None) as batch_op:
        batch_op.drop_index('ix_annotation_task_create_user')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('annotation_task', schema=None) as batch_op:
        batch_op.create_index('ix_annotation_task_create_user', ['create_user'], unique=False)

    # ### end Alembic commands ###

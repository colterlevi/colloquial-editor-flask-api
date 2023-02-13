"""empty message

Revision ID: 65a35fdcd309
Revises: 185fe660231d
Create Date: 2023-02-13 15:02:43.423580

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '65a35fdcd309'
down_revision = '185fe660231d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('articles', schema=None) as batch_op:
        batch_op.alter_column('tags',
               existing_type=postgresql.ARRAY(sa.INTEGER()),
               nullable=False)
        batch_op.alter_column('categories',
               existing_type=postgresql.ARRAY(sa.INTEGER()),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('articles', schema=None) as batch_op:
        batch_op.alter_column('categories',
               existing_type=postgresql.ARRAY(sa.INTEGER()),
               nullable=True)
        batch_op.alter_column('tags',
               existing_type=postgresql.ARRAY(sa.INTEGER()),
               nullable=True)

    # ### end Alembic commands ###
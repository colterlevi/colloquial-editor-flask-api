"""empty message

Revision ID: 9cdbb47866a5
Revises: 65a35fdcd309
Create Date: 2023-02-15 10:49:20.351530

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9cdbb47866a5'
down_revision = '65a35fdcd309'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('articles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image', sa.String(length=120), nullable=True))

    with op.batch_alter_table('authors', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image', sa.String(length=120), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('authors', schema=None) as batch_op:
        batch_op.drop_column('image')

    with op.batch_alter_table('articles', schema=None) as batch_op:
        batch_op.drop_column('image')

    # ### end Alembic commands ###

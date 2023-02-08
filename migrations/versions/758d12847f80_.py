"""empty message

Revision ID: 758d12847f80
Revises: 
Create Date: 2023-02-08 14:47:18.706414

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '758d12847f80'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('edits',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
    sa.ForeignKeyConstraint(['author_id'], ['authors.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('articles', schema=None) as batch_op:
        batch_op.alter_column('content',
               existing_type=sa.TEXT(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('articles', schema=None) as batch_op:
        batch_op.alter_column('content',
               existing_type=sa.TEXT(),
               nullable=False)

    op.drop_table('edits')
    # ### end Alembic commands ###

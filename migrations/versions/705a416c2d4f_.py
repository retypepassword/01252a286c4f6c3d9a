"""empty message

Revision ID: 705a416c2d4f
Revises: 
Create Date: 2024-05-05 07:16:17.204272

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '705a416c2d4f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute('create schema if not exists proposal')
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('physician',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('address', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    schema='proposal'
    )
    op.create_table('zip_code',
    sa.Column('zip', sa.String(), nullable=False),
    sa.Column('latitude', sa.Float(), nullable=False),
    sa.Column('longitude', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('zip'),
    schema='proposal'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('zip_code', schema='proposal')
    op.drop_table('physician', schema='proposal')
    op.execute('drop schema proposal')
    # ### end Alembic commands ###

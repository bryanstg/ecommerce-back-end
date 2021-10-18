"""empty message

Revision ID: ceebe9424c1f
Revises: 862e51bc93be
Create Date: 2021-06-24 21:28:41.083326

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ceebe9424c1f'
down_revision = '862e51bc93be'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('product', 'img_url',
               existing_type=sa.VARCHAR(length=360),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('product', 'img_url',
               existing_type=sa.VARCHAR(length=360),
               nullable=False)
    # ### end Alembic commands ###
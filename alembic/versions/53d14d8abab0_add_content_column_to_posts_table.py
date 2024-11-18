"""add content column to posts table

Revision ID: 53d14d8abab0
Revises: 233c1316c75d
Create Date: 2024-11-18 15:50:22.758712

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53d14d8abab0'
down_revision: Union[str, None] = '233c1316c75d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_column('posts', 'content')
    pass

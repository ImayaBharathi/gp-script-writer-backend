"""adding beatsheet id table for tasking ai

Revision ID: eb6c56f95dfa
Revises: 
Create Date: 2024-05-13 23:57:26.379025

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb6c56f95dfa'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

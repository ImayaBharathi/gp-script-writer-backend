"""adding a change in script_ai_table

Revision ID: e06f24450962
Revises: eb6c56f95dfa
Create Date: 2024-05-14 00:02:16.089452

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e06f24450962'
down_revision: Union[str, None] = 'eb6c56f95dfa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

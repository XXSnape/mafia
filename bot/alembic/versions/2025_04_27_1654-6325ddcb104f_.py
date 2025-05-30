"""empty message

Revision ID: 6325ddcb104f
Revises: 23b6fd1f7070
Create Date: 2025-04-27 16:54:26.084779

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6325ddcb104f"
down_revision: Union[str, None] = "23b6fd1f7070"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "settings",
        sa.Column(
            "show_usernames_during_voting",
            sa.Boolean(),
            server_default="1",
            nullable=False,
        ),
    )
    op.add_column(
        "settings",
        sa.Column(
            "mafia_every_3",
            sa.Boolean(),
            server_default="0",
            nullable=False,
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("settings", "mafia_every_3")
    op.drop_column("settings", "show_usernames_during_voting")
    # ### end Alembic commands ###

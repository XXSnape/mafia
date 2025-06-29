"""empty message

Revision ID: 841e244f58e8
Revises: 01d391646939
Create Date: 2025-06-23 17:27:48.711677

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "841e244f58e8"
down_revision: Union[str, None] = "01d391646939"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("settings")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "settings",
        sa.Column(
            "user_tg_id",
            sa.BIGINT(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "time_for_night",
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "time_for_day",
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "id", sa.INTEGER(), autoincrement=True, nullable=False
        ),
        sa.Column(
            "show_killers",
            sa.BOOLEAN(),
            server_default=sa.text("true"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "show_information_about_guests_at_night",
            sa.BOOLEAN(),
            server_default=sa.text("true"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "can_kill_teammates",
            sa.BOOLEAN(),
            server_default=sa.text("true"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "can_marshal_kill",
            sa.BOOLEAN(),
            server_default=sa.text("true"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "show_usernames_during_voting",
            sa.BOOLEAN(),
            server_default=sa.text("true"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "mafia_every_3",
            sa.BOOLEAN(),
            server_default=sa.text("false"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "time_for_voting",
            sa.INTEGER(),
            server_default=sa.text("35"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "time_for_confirmation",
            sa.INTEGER(),
            server_default=sa.text("35"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "show_usernames_after_confirmation",
            sa.BOOLEAN(),
            server_default=sa.text("false"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "show_roles_after_death",
            sa.BOOLEAN(),
            server_default=sa.text("true"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "show_peaceful_allies",
            sa.BOOLEAN(),
            server_default=sa.text("true"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "allow_betting",
            sa.BOOLEAN(),
            server_default=sa.text("true"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "speed_up_nights_and_voting",
            sa.BOOLEAN(),
            server_default=sa.text("false"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "protect_content",
            sa.BOOLEAN(),
            server_default=sa.text("false"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "can_talk_at_night",
            sa.BOOLEAN(),
            server_default=sa.text("true"),
            autoincrement=False,
            nullable=False,
        ),
        sa.CheckConstraint(
            "time_for_day > 10", name="settings_time_for_day_check"
        ),
        sa.CheckConstraint(
            "time_for_night > 10",
            name="settings_time_for_night_check",
        ),
        sa.ForeignKeyConstraint(
            ["user_tg_id"],
            ["users.tg_id"],
            name="settings_user_tg_id_fkey",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="settings_pkey"),
    )
    # ### end Alembic commands ###

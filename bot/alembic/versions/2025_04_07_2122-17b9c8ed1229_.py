"""empty message

Revision ID: 17b9c8ed1229
Revises:
Create Date: 2025-04-07 21:22:35.094356

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "17b9c8ed1229"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "groupings",
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("name"),
    )
    op.create_table(
        "users",
        sa.Column(
            "tg_id",
            sa.BigInteger(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "balance",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "registration_date",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_banned", sa.Boolean(), nullable=False),
        sa.CheckConstraint("balance >= 0"),
        sa.PrimaryKeyConstraint("tg_id"),
    )
    op.create_table(
        "roles",
        sa.Column(
            "key",
            sa.Enum(
                "don",
                "doctor",
                "policeman",
                "traitor",
                "killer",
                "werewolf",
                "forger",
                "hacker",
                "sleeper",
                "agent",
                "journalist",
                "punisher",
                "analyst",
                "suicide_bomber",
                "instigator",
                "prime_minister",
                "bodyguard",
                "masochist",
                "lawyer",
                "angel_of_death",
                "prosecutor",
                "civilian",
                "lucky_gay",
                "mafia",
                "nurse",
                "general",
                "warden",
                "poisoner",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("grouping", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["grouping"], ["groupings.name"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("key"),
    )
    op.create_table(
        "settings",
        sa.Column("user_tg_id", sa.BigInteger(), nullable=False),
        sa.Column("time_for_night", sa.Integer(), nullable=False),
        sa.Column("time_for_day", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.CheckConstraint("time_for_day > 10"),
        sa.CheckConstraint("time_for_night > 10"),
        sa.ForeignKeyConstraint(
            ["user_tg_id"], ["users.tg_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "groups",
        sa.Column("tg_id", sa.BigInteger(), nullable=False),
        sa.Column("setting_id", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["setting_id"], ["settings.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tg_id"),
    )
    op.create_table(
        "orders",
        sa.Column("user_tg_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "role_id",
            sa.Enum(
                "don",
                "doctor",
                "policeman",
                "traitor",
                "killer",
                "werewolf",
                "forger",
                "hacker",
                "sleeper",
                "agent",
                "journalist",
                "punisher",
                "analyst",
                "suicide_bomber",
                "instigator",
                "prime_minister",
                "bodyguard",
                "masochist",
                "lawyer",
                "angel_of_death",
                "prosecutor",
                "civilian",
                "lucky_gay",
                "mafia",
                "nurse",
                "general",
                "warden",
                "poisoner",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.CheckConstraint("number > 0"),
        sa.ForeignKeyConstraint(
            ["role_id"], ["roles.key"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_tg_id"], ["users.tg_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "prohibited_roles",
        sa.Column("user_tg_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "role_id",
            sa.Enum(
                "don",
                "doctor",
                "policeman",
                "traitor",
                "killer",
                "werewolf",
                "forger",
                "hacker",
                "sleeper",
                "agent",
                "journalist",
                "punisher",
                "analyst",
                "suicide_bomber",
                "instigator",
                "prime_minister",
                "bodyguard",
                "masochist",
                "lawyer",
                "angel_of_death",
                "prosecutor",
                "civilian",
                "lucky_gay",
                "mafia",
                "nurse",
                "general",
                "warden",
                "poisoner",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["role_id"], ["roles.key"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_tg_id"], ["users.tg_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "games",
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.Column("winning_group", sa.String(), nullable=True),
        sa.Column("number_of_nights", sa.Integer(), nullable=True),
        sa.Column("start", sa.DateTime(), nullable=False),
        sa.Column("end", sa.DateTime(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"], ["groups.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["winning_group"],
            ["groupings.name"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "rates",
        sa.Column("money", sa.Integer(), nullable=False),
        sa.Column("is_winner", sa.Boolean(), nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("user_tg_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "role_id",
            sa.Enum(
                "don",
                "doctor",
                "policeman",
                "traitor",
                "killer",
                "werewolf",
                "forger",
                "hacker",
                "sleeper",
                "agent",
                "journalist",
                "punisher",
                "analyst",
                "suicide_bomber",
                "instigator",
                "prime_minister",
                "bodyguard",
                "masochist",
                "lawyer",
                "angel_of_death",
                "prosecutor",
                "civilian",
                "lucky_gay",
                "mafia",
                "nurse",
                "general",
                "warden",
                "poisoner",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.CheckConstraint("money > 0"),
        sa.ForeignKeyConstraint(
            ["game_id"], ["games.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["role_id"], ["roles.key"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_tg_id"], ["users.tg_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "results",
        sa.Column("user_tg_id", sa.BigInteger(), nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column(
            "role_id",
            sa.Enum(
                "don",
                "doctor",
                "policeman",
                "traitor",
                "killer",
                "werewolf",
                "forger",
                "hacker",
                "sleeper",
                "agent",
                "journalist",
                "punisher",
                "analyst",
                "suicide_bomber",
                "instigator",
                "prime_minister",
                "bodyguard",
                "masochist",
                "lawyer",
                "angel_of_death",
                "prosecutor",
                "civilian",
                "lucky_gay",
                "mafia",
                "nurse",
                "general",
                "warden",
                "poisoner",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("is_winner", sa.Boolean(), nullable=False),
        sa.Column("nights_lived", sa.Integer(), nullable=False),
        sa.Column("money", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.CheckConstraint("money >= 0"),
        sa.ForeignKeyConstraint(
            ["game_id"], ["games.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["role_id"], ["roles.key"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["user_tg_id"], ["users.tg_id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("results")
    op.drop_table("rates")
    op.drop_table("games")
    op.drop_table("prohibited_roles")
    op.drop_table("orders")
    op.drop_table("groups")
    op.drop_table("settings")
    op.drop_table("roles")
    op.drop_table("users")
    op.drop_table("groupings")
    # ### end Alembic commands ###

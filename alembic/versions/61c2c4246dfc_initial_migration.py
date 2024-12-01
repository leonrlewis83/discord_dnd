"""Initial migration

Revision ID: 61c2c4246dfc
Revises: 
Create Date: 2024-12-01 22:23:26.232072+00:00

"""
from typing import Sequence, Union
from sqlalchemy.orm import Session
from alembic import op
import sqlalchemy as sa
from models.ReferenceTables import ClassEnumDB, RacesEnumDB, StatsEnumDB
from entities.Classes import ClassEnum
from entities.Races import RacesEnum
from entities.Stats import StatsEnum


# revision identifiers, used by Alembic.
revision: str = '61c2c4246dfc'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create reference tables first
    op.create_table(
        'class_ref',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('display_name', sa.String, nullable=False, unique=True),
    )

    op.create_table(
        'races_ref',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('display_name', sa.String, nullable=False, unique=True),
    )

    op.create_table(
        'stats_ref',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('display_name', sa.String, nullable=False, unique=True),
        sa.Column('abbr', sa.String, nullable=False, unique=True),
        sa.Column('description', sa.String, nullable=False),
    )

    # Create dependent tables
    op.create_table(
        'characters',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('level', sa.Integer, nullable=False, default=1),
        sa.Column('class_id', sa.Integer, sa.ForeignKey('class_ref.id'), nullable=False),
        sa.Column('race_id', sa.Integer, sa.ForeignKey('races_ref.id'), nullable=False),
        sa.Column('stats', sa.JSON, nullable=False),
    )

    op.create_table(
        'inventories',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('character_id', sa.Integer, sa.ForeignKey('characters.id'), nullable=False),
        sa.Column('item_name', sa.String, nullable=False),
        sa.Column('quantity', sa.Integer, nullable=False, default=1),
    )

    # Populate reference tables
    bind = op.get_bind()
    session = Session(bind=bind)

    # Insert into class_enum
    for enum in ClassEnum:
        session.add(ClassEnumDB(display_name=enum.display_name))

    # Insert into races_enum
    for enum in RacesEnum:
        session.add(RacesEnumDB(display_name=enum.display_name))

    # Insert into stats_enum
    for enum in StatsEnum:
        session.add(StatsEnumDB(
            display_name=enum.display_name,
            abbr=enum.abbr,
            description=enum.description
        ))

    # Commit the session
    session.commit()


def downgrade():
    # Drop tables in reverse order
    op.drop_table('inventories')
    op.drop_table('characters')
    op.drop_table('stats_enum')
    op.drop_table('races_enum')
    op.drop_table('class_enum')

"""Add user_id to characters table

Revision ID: 6bd941238fcf
Revises: 61c2c4246dfc
Create Date: 2024-12-01 23:29:25.147937+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6bd941238fcf'
down_revision: Union[str, None] = '61c2c4246dfc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('character_inventory',
    sa.Column('character_id', sa.Integer(), nullable=False),
    sa.Column('item_name', sa.String(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['character_id'], ['characters.id'], ),
    sa.PrimaryKeyConstraint('character_id', 'item_name')
    )
    op.add_column('characters', sa.Column('user_id', sa.Integer(), nullable=False))
    op.add_column('characters', sa.Column('chosen_class_id', sa.Integer(), nullable=False))
    op.add_column('characters', sa.Column('chosen_race_id', sa.Integer(), nullable=False))
    op.add_column('characters', sa.Column('completed', sa.Boolean(), nullable=False))
    op.drop_constraint('characters_class_id_fkey', 'characters', type_='foreignkey')
    op.drop_constraint('characters_race_id_fkey', 'characters', type_='foreignkey')
    op.create_foreign_key(None, 'characters', 'class_ref', ['chosen_class_id'], ['id'])
    op.create_foreign_key(None, 'characters', 'races_ref', ['chosen_race_id'], ['id'])
    op.drop_column('characters', 'race_id')
    op.drop_column('characters', 'class_id')
    op.drop_column('characters', 'level')
    op.add_column('inventories', sa.Column('items', sa.JSON(), nullable=True))
    op.drop_constraint('inventories_character_id_fkey', 'inventories', type_='foreignkey')
    op.drop_column('inventories', 'character_id')
    op.drop_column('inventories', 'quantity')
    op.drop_column('inventories', 'item_name')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('inventories', sa.Column('item_name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('inventories', sa.Column('quantity', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('inventories', sa.Column('character_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('inventories_character_id_fkey', 'inventories', 'characters', ['character_id'], ['id'])
    op.drop_column('inventories', 'items')
    op.add_column('characters', sa.Column('level', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('characters', sa.Column('class_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('characters', sa.Column('race_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'characters', type_='foreignkey')
    op.drop_constraint(None, 'characters', type_='foreignkey')
    op.create_foreign_key('characters_race_id_fkey', 'characters', 'races_ref', ['race_id'], ['id'])
    op.create_foreign_key('characters_class_id_fkey', 'characters', 'class_ref', ['class_id'], ['id'])
    op.drop_column('characters', 'completed')
    op.drop_column('characters', 'chosen_race_id')
    op.drop_column('characters', 'chosen_class_id')
    op.drop_column('characters', 'user_id')
    op.drop_table('character_inventory')
    # ### end Alembic commands ###
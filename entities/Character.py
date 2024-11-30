from discord.mentions import default
from sqlalchemy import Column, Integer, String, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from dataclasses import dataclass, field
from typing import Dict, Optional
from entities.Stats import StatsEnum
from entities.Races import RacesEnum
from entities.Classes import ClassEnum

Base = declarative_base()
# Lost Logging - need to implement eventually
# Association table for many-to-many relationships (e.g., inventory items)
character_inventory = Table(
    "character_inventory",
    Base.metadata,
    Column("character_id", Integer, ForeignKey("characters.id"), primary_key=True),
    Column("item_name", String, primary_key=True),
    Column("quantity", Integer, nullable=False, default=1),
)

class Inventory(Base):
    """
    SQLAlchemy ORM representation for Inventory.
    """
    __tablename__ = "inventories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    items = Column(JSON, default={})  # Store as JSON for flexibility

@dataclass
class Character(Base):
    """
    SQLAlchemy ORM representation for Characters.
    """
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    stats: Mapped[Dict[str, int]] = mapped_column(JSON, nullable=False)  # Store stats as JSON
    chosen_class: Mapped[str] = mapped_column(String, nullable=False)  # Store class name
    chosen_race: Mapped[str] = mapped_column(String, nullable=False)  # Store race name
    completed: Mapped[bool] = mapped_column(nullable=False, default=False)

    # Relationship with inventory
    inventory: Mapped[Inventory] = relationship("Inventory", backref="character", uselist=False)

    def __init__(self, user_id):
        self.user_id = user_id

    def validate(self):
        """
        Ensure the character is fully constructed before saving.
        Raises:
            ValueError: If any required field is missing.
        """
        if not self.stats or not isinstance(self.stats, dict) or len(self.stats) != len(StatsEnum):
            raise ValueError("Stats are incomplete or invalid.")
        if not self.chosen_class or not isinstance(self.chosen_class, ClassEnum):
            raise ValueError("Class is not selected or invalid.")
        if not self.chosen_race or not isinstance(self.chosen_race, RacesEnum):
            raise ValueError("Race is not selected or invalid.")
        if not self.name or not isinstance(self.name, str) or len(self.name) < 1:
            raise ValueError("Name is invalid.")

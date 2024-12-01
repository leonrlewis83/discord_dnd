from discord.mentions import default
from sqlalchemy import Column, Integer, String, ForeignKey, Table, JSON, Boolean
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

@dataclass
class Character(Base):
    """
    SQLAlchemy ORM representation for Characters.
    """
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    name =  Column(String, nullable=False)
    stats = Column(JSON, nullable=False)  # Store stats as JSON
    chosen_class_id = Column(Integer, ForeignKey('class_enum.id'), nullable=False)
    chosen_race_id = Column(Integer, ForeignKey('races_enum.id'), nullable=False)
    completed = Column(Boolean, nullable=False, default=False)

    # Relationships
    chosen_class = relationship("ClassEnumDB")
    chosen_race = relationship("RacesEnumDB")

    # Relationship with inventory
    # inventory: Mapped[Inventory] = relationship("Inventory", backref="character", uselist=False)

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

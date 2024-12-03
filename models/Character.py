import logging
from sqlalchemy import Column, Integer, String, ForeignKey, Table, JSON, Boolean, BigInteger
from sqlalchemy.orm import relationship
from dataclasses import dataclass
from models.ReferenceTables import ClassEnumDB, RacesEnumDB
from entities.Stats import StatsEnum
from entities.Races import RacesEnum
from entities.Classes import ClassEnum
from models.base import Base

logger = logging.getLogger("bot.character.object")
# Association table for many-to-many relationships (e.g., inventory items)

@dataclass
class Character(Base):
    """
    SQLAlchemy ORM representation for Characters.
    """
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    name =  Column(String, nullable=False)
    stats = Column(JSON, nullable=True)  # Store stats as JSON
    chosen_class_id = Column(Integer, ForeignKey('class_ref.id'), nullable=True)
    chosen_race_id = Column(Integer, ForeignKey('races_ref.id'), nullable=True)
    completed = Column(Boolean, nullable=False, default=False)

    # Relationships
    chosen_class = relationship(ClassEnumDB, backref="characters")
    chosen_race = relationship(RacesEnumDB, backref="characters")

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
            logger.debug(f"{self.stats}")
            raise ValueError("Stats are incomplete or invalid.")
        if not self.chosen_class or not isinstance(self.chosen_class, ClassEnum):
            logger.debug(f"{self.chosen_class}")
            raise ValueError("Class is not selected or invalid.")
        if not self.chosen_race or not isinstance(self.chosen_race, RacesEnum):
            logger.debug(f"{self.chosen_race}")
            raise ValueError("Race is not selected or invalid.")
        if not self.name or not isinstance(self.name, str) or len(self.name) < 1:
            logger.debug(f"{self.name}")
            raise ValueError("Name is invalid.")

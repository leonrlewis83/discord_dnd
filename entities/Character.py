from dataclasses import dataclass, field
from typing import Dict, Optional
from entities.Stats import StatsEnum
from entities.Races import RacesEnum
from entities.Classes import ClassEnum

# TODO: Fully implement inventory tracking
@dataclass
class Inventory:
    items: Dict[str, int] = field(default_factory=dict) # Item and quantity

@dataclass
class Race:
    name: RacesEnum
    stat_offsets: Dict[StatsEnum, int] = field(default_factory=dict)

@dataclass
class Class:
    name: ClassEnum

@dataclass
class CharacterBuilder:
    character_name: str
    user_id: int
    stats: Optional[Dict[StatsEnum, int]] = None
    chosen_class: Optional[ClassEnum] = None
    chosen_race: Optional[RacesEnum] = None

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

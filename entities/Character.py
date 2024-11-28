from dataclasses import dataclass, field
from typing import Dict
from Classes import ClassEnum
from Stats import StatsEnum

# TODO: Fully implement inventory tracking
@dataclass
class Inventory:
    items: Dict[str, int] = field(default_factory=dict) # Item and quantity

@dataclass
class Race:
    name: str
    stat_offsets: Dict[StatsEnum, int] = field(default_factory=dict)

@dataclass
class Class:
    name: ClassEnum

@dataclass
class Character:
    name: str
    char_race: Race
    stats: Dict[StatsEnum, int] = field(default_factory=dict)

from enum import Enum

class StatsEnum(Enum):
    STRENGTH = ("Strength", "STR", "Physical power and muscle")
    DEXTERITY = ("Dexterity", "DEX", "Agility and reflexes")
    CONSTITUTION = ("Constitution", "CON", "Endurance and stamina")
    INTELLIGENCE = ("Intelligence", "INT", "Memory and reasoning")
    WISDOM = ("Wisdom", "WIS", "Perception and insight")
    CHARISMA = ("Charisma", "CHA", "Influence and charm")

    def __init__(self, display_name, abbr, description):
        self.display_name = display_name
        self.abbr = abbr
        self.description = description

    @classmethod
    def list(cls):
        """Return a list of all race names."""
        return [stat.display_name for stat in cls]
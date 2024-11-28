from enum import Enum

class ClassEnum(Enum):
    BARBARIAN = ("Barbarian")
    BARD = ("Bard")
    CLERIC = ("Cleric")
    DRUID = ("Druid")
    FIGHTER = ("Fighter")
    MONK = ("Monk")
    PALADIN = ("Paladin")
    RANGER = ("Ranger")
    ROGUE = ("Rogue")
    SORCERER = ("Sorcerer")
    WARLOCK = ("Warlock")
    WIZARD = ("Wizard")

    def __init__(self, display_name):
        self.display_name = display_name
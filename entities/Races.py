from enum import Enum

class RacesEnum(Enum):
    AASIMAR = "Aasimar"
    DRAGONBORN = "Dragonborn"
    DWARF = "Dwarf"
    ELF = "Elf"
    GNOME = "Gnome"
    GOLIATH = "Goliath"
    HALFLING = "Halfling"
    HUMAN = "Human"
    ORC = "Orc"
    TIEFLING = "Tiefling"

    @classmethod
    def list(cls):
        """Return a list of all race names."""
        return [race.value for race in cls]

from spells.level_1 import guiding_bolt, heroism

class Oath:
    """A base class for all Paladin Oaths."""
    def __init__(self, name):
        self.name = name

    def get_oath_spells(self, paladin_level):
        """Returns a list of spells granted by the oath at a given level."""
        return []

class OathOfGlory(Oath):
    """The Oath of Glory subclass."""
    def __init__(self):
        super().__init__("Oath of Glory")

    def get_oath_spells(self, paladin_level):
        spells = []
        if paladin_level >= 3:
            # According to the PHB, Oath of Glory grants these at level 3
            spells.extend([guiding_bolt, heroism])
        # In a more complete simulation, we would add spells for levels 5, 9, etc.
        return spells


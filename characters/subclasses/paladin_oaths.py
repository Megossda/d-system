# File: characters/subclasses/paladin_oaths.py
from spells.level_1.heroism import heroism
from spells.level_1.guiding_bolt import guiding_bolt  # PHB 2024 version


# Remove guiding_bolt import - it's legacy

class Oath:
    """A base class for all Paladin Oaths."""

    def __init__(self, name):
        self.name = name

    def get_oath_spells(self, paladin_level):
        """Returns a list of spells granted by the oath at a given level."""
        return []


class OathOfGlory(Oath):
    """The Oath of Glory subclass - PHB 2024 version."""

    def __init__(self):
        super().__init__("Oath of Glory")

    def get_oath_spells(self, paladin_level):
        spells = []
        if paladin_level >= 3:
            # PHB 2024: Oath of Glory 3rd level spells
            # Note: Need to check actual PHB 2024 for correct spells
            # Removing guiding_bolt as it's legacy
            spells.extend([heroism])  # Keep heroism, add correct 2024 spells

        # TODO: Add correct PHB 2024 Oath of Glory spells
        # Level 5, 9, 13, 17 spells need to be added
        return spells

    def get_channel_divinity_options(self, paladin_level):
        """Oath of Glory Channel Divinity options."""
        options = []

        if paladin_level >= 3:
            from systems.paladin.oath_of_glory_channel_divinity import InspiringSMiteOption, PeerlessAthleteOption
            options.extend([
                InspiringSMiteOption(),
                PeerlessAthleteOption()
            ])

        return options
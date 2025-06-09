# File: spells/level_1/searing_smite.py
from ..base_spell import Spell

class SearingSmite(Spell):
    def __init__(self):
        super().__init__(name="Searing Smite", level=1, school="Evocation", casting_time="1 Bonus Action",
                         requires_concentration=True, damage_type="Fire")

    def cast(self, caster, target=None):
        caster.active_smites.append(self)
        if self.requires_concentration:
            caster.start_concentrating(self)
        return True

# Create the instance
searing_smite = SearingSmite()
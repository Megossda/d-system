# File: spells/level_1/bless.py
from ..base_spell import Spell

class Bless(Spell):
    def __init__(self):
        super().__init__(name="Bless", level=1, school="Enchantment", requires_concentration=True)

    def cast(self, caster, target=None):
        # In a full implementation, this would affect multiple targets and add 1d4 to their attack rolls and saves.
        print(f"** {caster.name}'s allies feel divinely favored! **")
        caster.start_concentrating(self)
        return True

# Create the instance
bless = Bless()
# File: spells/level_1/heroism.py
from ..base_spell import Spell

class Heroism(Spell):
    """The Heroism spell."""

    def __init__(self):
        super().__init__(name="Heroism", level=1, school="Enchantment", requires_concentration=True)

    def cast(self, caster, target=None):
        """A creature you touch is imbued with bravery."""
        target_to_affect = target or caster
        print(f"** {target_to_affect.name} is imbued with bravery and feels heroic! **")
        # In a full implementation, this would grant temporary HP each round.
        caster.start_concentrating(self)
        return True

# Create the instance
heroism = Heroism()
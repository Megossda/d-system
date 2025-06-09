# File: spells/level_1/cure_wounds.py
from ..base_spell import Spell
from core import roll

class CureWounds(Spell):
    def __init__(self):
        super().__init__(name="Cure Wounds", level=1, school="Abjuration")

    def cast(self, caster, target):
        if not target:
            return False

        healing_amount = roll('1d8') + caster.get_spellcasting_modifier()
        original_hp = target.hp
        target.hp = min(target.max_hp, target.hp + healing_amount)
        healed_for = target.hp - original_hp

        print(f"** {caster.name} heals {target.name} for {healed_for} HP! **")
        print(f"{target.name}'s HP is now {target.hp}/{target.max_hp}.")
        return True

# Create the instance
cure_wounds = CureWounds()
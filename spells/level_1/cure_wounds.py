# File: spells/level_1/cure_wounds.py
from ..base_spell import Spell
from core import roll


class CureWounds(Spell):
    def __init__(self):
        super().__init__(
            name="Cure Wounds",
            level=1,
            school="Abjuration",
            casting_time="1 Action",
            attack_save="None"
        )

    def cast(self, caster, target, spell_level=1):
        """PHB 2024: 2d8 + spellcasting modifier, +2d8 per higher level."""
        if not target:
            return False

        # PHB 2024: Base healing is 2d8 (not 1d8)
        base_dice = 2

        # Higher level casting: +2d8 per level above 1st
        if spell_level > 1:
            total_dice = base_dice + (2 * (spell_level - 1))
        else:
            total_dice = base_dice

        # Roll the healing dice
        healing_roll = 0
        for _ in range(total_dice):
            healing_roll += roll('1d8')

        # Add spellcasting modifier
        spell_mod = caster.get_spellcasting_modifier()
        healing_amount = healing_roll + spell_mod

        # Apply healing
        original_hp = target.hp
        target.hp = min(target.max_hp, target.hp + healing_amount)
        healed_for = target.hp - original_hp

        # Log the healing with proper breakdown
        dice_text = f"{total_dice}d8" if spell_level == 1 else f"{total_dice}d8 (upcast from 2d8)"
        print(f"** {caster.name} heals {target.name} for {healed_for} HP! **")
        print(f"   Healing: {healing_roll} [{dice_text}] +{spell_mod} [CHA] = {healing_amount} total")
        print(f"   {target.name}'s HP: {original_hp} → {target.hp}/{target.max_hp}")

        return True


# Create the instance
cure_wounds = CureWounds()
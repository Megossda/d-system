# File: spells/level_1/divine_smite.py
from ..base_spell import Spell
from core import roll

class DivineSmite(Spell):
    """Divine Smite spell - PHB 2024 version. Cast as bonus action after hitting with melee attack."""

    def __init__(self):
        super().__init__(
            name="Divine Smite",
            level=1,
            school="Evocation",
            casting_time="1 Bonus Action (after hitting with melee attack)",
            damage_type="Radiant",
            attack_save="None"
        )

    def cast(self, caster, target, spell_level=1, is_crit=False):
        """
        Cast Divine Smite immediately after hitting with a melee weapon or unarmed strike.
        spell_level: The level of spell slot used (1-5)
        is_crit: Whether the triggering attack was a critical hit
        """
        if not target:
            return False

        # PHB 2024: Base damage 2d8, +1d8 per higher level
        base_dice_count = 2  # Always starts with 2d8
        bonus_dice = spell_level - 1  # +1d8 per level above 1st
        total_dice_count = base_dice_count + bonus_dice

        # Roll base damage
        damage = 0
        for _ in range(total_dice_count):
            damage += roll('1d8')

        damage_description = f"{total_dice_count}d8"
        if spell_level > 1:
            damage_description += f" (2d8 base +{bonus_dice}d8 upcast)"

        # Critical hit doubles ALL smite dice
        if is_crit:
            crit_damage = 0
            for _ in range(total_dice_count):
                crit_damage += roll('1d8')
            damage += crit_damage
            damage_description = f"{total_dice_count * 2}d8 CRIT from {damage_description}"

        # PHB 2024: Extra 1d8 damage vs Undead/Fiends
        extra_damage = 0
        if hasattr(target, 'creature_type'):
            if target.creature_type in ['Undead', 'Fiend']:
                extra_damage = roll('1d8')
                if is_crit:
                    extra_damage += roll('1d8')  # Crit doubles this too
                damage += extra_damage
                crit_text = " CRIT" if is_crit else ""
                damage_description += f" +{extra_damage} [vs {target.creature_type}{crit_text}]"

        print(f"** DIVINE SMITE: {damage} radiant damage ({damage_description}) **")
        target.take_damage(damage, attacker=caster)
        return True

# Create the instance
divine_smite = DivineSmite()
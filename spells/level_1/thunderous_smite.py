# File: spells/level_1/thunderous_smite.py
from ..base_spell import Spell
from core import roll


class ThunderousSmite(Spell):
    """Thunderous Smite spell - thunder damage with knockback and prone."""

    def __init__(self):
        super().__init__(
            name="Thunderous Smite",
            level=1,
            school="Evocation",
            casting_time="1 Bonus Action (after hitting with melee attack)",
            damage_type="Thunder",
            attack_save="STR Save"
        )

    def cast(self, caster, target, spell_level=1):
        """PHB 2024: Immediate thunder damage + knockback/prone effect."""
        if not target:
            return False

        # PHB 2024: Base damage 2d6, +1d6 per higher level
        base_dice = 2
        bonus_dice = spell_level - 1
        total_dice = base_dice + bonus_dice

        # Roll thunder damage
        damage = 0
        for _ in range(total_dice):
            damage += roll('1d6')

        damage_text = f"{total_dice}d6"
        if spell_level > 1:
            damage_text += f" (2d6 base +{bonus_dice}d6 upcast)"

        print(f"** THUNDEROUS SMITE: {damage} thunder damage ({damage_text}) **")
        target.take_damage(damage, attacker=caster)

        # Thunderclap effect - audible at 300 feet
        print(f"** A thunderous boom echoes from the strike, audible within 300 feet! **")

        # PHB 2024: Strength save or be pushed 10 feet + knocked prone
        if target.is_alive:
            save_dc = caster.get_spell_save_dc()
            print(f"** {target.name} must make a DC {save_dc} Strength saving throw! **")

            if not target.make_saving_throw('str', save_dc):
                print(f"** {target.name} is pushed 10 feet away and knocked prone! **")

                # Apply knockback (move target away from caster)
                direction = 1 if target.position > caster.position else -1
                target.position += (10 * direction)
                print(f"** {target.name} is pushed to position {target.position}ft **")

                # Apply prone condition
                if not hasattr(target, 'is_prone'):
                    target.is_prone = False
                target.is_prone = True
                print(f"** {target.name} falls prone! **")
            else:
                print(f"** {target.name} resists the thunderous force and keeps their footing! **")

        if spell_level > 1:
            print(f"** Upcast at level {spell_level} for extra damage **")

        return True


# Create the instance
thunderous_smite = ThunderousSmite()
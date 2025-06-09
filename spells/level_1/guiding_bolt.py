# File: spells/level_1/guiding_bolt.py
from ..base_spell import Spell
from core import roll


class GuidingBolt(Spell):
    """Guiding Bolt spell - PHB 2024 version."""

    def __init__(self):
        super().__init__(
            name="Guiding Bolt",
            level=1,
            school="Evocation",
            casting_time="1 Action",
            attack_save="Ranged",
            damage_type="Radiant"
        )

    def cast(self, caster, target, spell_level=1):
        """PHB 2024: 4d6 radiant + advantage to next attacker, +1d6 per higher level."""
        if not target:
            return False

        # Make ranged spell attack
        is_hit = caster.make_spell_attack(target, self)
        if is_hit:
            # PHB 2024: Base damage 4d6, +1d6 per spell level above 1st
            base_dice = 4
            bonus_dice = spell_level - 1
            total_dice = base_dice + bonus_dice

            # Roll damage
            damage = 0
            for _ in range(total_dice):
                damage += roll('1d6')

            damage_text = f"{total_dice}d6"
            if spell_level > 1:
                damage_text += f" (4d6 base +{bonus_dice}d6 upcast)"

            print(
                f"** The {self.name} strikes {target.name} for {damage} {self.damage_type} damage! ({damage_text}) **")
            target.take_damage(damage, attacker=caster)

            if target.is_alive:
                # PHB 2024: Next attack has advantage until end of your next turn
                target.grants_advantage_to_next_attacker = True
                target.advantage_expires_round = getattr(caster, 'current_round', 1) + 1  # Next round
                print(f"** {target.name} is shimmering with mystical light! **")
                print(
                    f"** The next attack roll against {target.name} before the end of your next turn has Advantage **")

                if spell_level > 1:
                    print(f"** Upcast at level {spell_level} for extra damage **")
        else:
            print(f"** The bolt of light misses {target.name} **")

        return True


# Create the instance
guiding_bolt = GuidingBolt()
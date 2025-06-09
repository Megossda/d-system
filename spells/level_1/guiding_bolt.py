# File: spells/level_1/guiding_bolt.py
from ..base_spell import Spell
from core import roll


class GuidingBolt(Spell):
    """The Guiding Bolt spell with FIXED advantage tracking and critical hits."""

    def __init__(self):
        super().__init__(name="Guiding Bolt", level=1, school="Evocation", attack_save="Ranged", damage_type="Radiant")

    def cast(self, caster, target):
        """Hurls a bolt of light that deals damage and makes the target easier to hit."""
        if not target:
            return False

        is_hit, is_crit = caster.make_spell_attack(target, self)
        if is_hit:
            if is_crit:
                print(">>> CRITICAL HIT! <<<")

            damage = roll('4d6')
            damage_log = "4d6"

            if is_crit:
                crit_damage = roll('4d6')
                damage += crit_damage
                damage_log = "8d6 (4d6 + 4d6 crit)"

            print(f"** The {self.name} strikes {target.name} for {damage} {self.damage_type} damage! ({damage_log}) **")
            target.take_damage(damage, attacker=caster)

            if target.is_alive:
                target.grants_advantage_to_next_attacker = True
                target.advantage_expires_round = getattr(caster, 'current_round', 1) + 1
                print(f"** {target.name} is shimmering with light, the next attack roll against it has Advantage. **")
        return True


# Create the instance
guiding_bolt = GuidingBolt()
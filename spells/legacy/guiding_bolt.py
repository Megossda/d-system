# File: spells/legacy/guiding_bolt.py
"""Legacy spell from 2014 PHB - not part of PHB 2024."""

from ..base_spell import Spell
from core import roll

class GuidingBolt(Spell):
    """Legacy Guiding Bolt spell from 2014 PHB."""

    def __init__(self):
        super().__init__(
            name="Guiding Bolt (Legacy)",
            level=1,
            school="Evocation",
            attack_save="Ranged",
            damage_type="Radiant"
        )

    def cast(self, caster, target):
        """Hurls a bolt of light that deals damage and grants advantage."""
        if not target:
            return False

        is_hit = caster.make_spell_attack(target, self)
        if is_hit:
            damage = roll('4d6')
            print(f"** The {self.name} strikes {target.name} for {damage} {self.damage_type} damage! **")
            target.take_damage(damage, attacker=caster)

            if target.is_alive:
                target.grants_advantage_to_next_attacker = True
                target.advantage_expires_round = getattr(caster, 'current_round', 1) + 1
                print(f"** {target.name} is shimmering with light, the next attack roll against it has Advantage. **")
        return True

# Create the instance (for backwards compatibility)
guiding_bolt = GuidingBolt()
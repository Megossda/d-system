# File: actions/__init__.py
"""Combat actions and abilities."""

from .base_actions import Action, AttackAction, DodgeAction, OpportunityAttack
from .spell_actions import CastSpellAction
from .special_actions import LayOnHandsAction, MultiattackAction

__all__ = [
    'Action', 'AttackAction', 'DodgeAction', 'OpportunityAttack',
    'CastSpellAction', 'LayOnHandsAction', 'MultiattackAction'
]

# File: actions/base_actions.py
class Action:
    """Base class for all actions."""
    def __init__(self, name):
        self.name = name

    def execute(self, performer, target=None, action_type="ACTION"):
        raise NotImplementedError

class AttackAction(Action):
    """An action that represents a weapon attack."""
    def __init__(self, weapon):
        super().__init__(f"Attack with {weapon.name}")
        self.weapon = weapon

    def execute(self, performer, target, action_type="ACTION"):
        performer.attack(target, action_type, weapon=self.weapon)

class DodgeAction(Action):
    def __init__(self):
        super().__init__("Dodge")

    def execute(self, performer, target=None, action_type="ACTION"):
        print(f"{action_type}: {performer.name} takes the Dodge action.")
        pass

class OpportunityAttack(Action):
    def __init__(self):
        super().__init__("Opportunity Attack")

    def execute(self, performer, target, action_type="REACTION"):
        print(f"** {performer.name} takes an Opportunity Attack against {target.name}! **")
        performer.attack(target, action_type)



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

# File: spells/level_1/guiding_bolt.py
from ..base_spell import Spell
from core import roll

class GuidingBolt(Spell):
    """The Guiding Bolt spell with FIXED advantage tracking."""

    def __init__(self):
        super().__init__(name="Guiding Bolt", level=1, school="Evocation", attack_save="Ranged", damage_type="Radiant")

    def cast(self, caster, target):
        """Hurls a bolt of light that deals damage and makes the target easier to hit."""
        if not target:
            return False

        is_hit = caster.make_spell_attack(target, self)
        if is_hit:
            damage = roll('4d6')
            print(f"** The {self.name} strikes {target.name} for {damage} {self.damage_type} damage! **")
            target.take_damage(damage, attacker=caster)

            if target.is_alive:
                # FIXED: Set advantage with proper expiration tracking
                target.grants_advantage_to_next_attacker = True
                target.advantage_expires_round = getattr(caster, 'current_round', 1) + 1  # Next round
                print(f"** {target.name} is shimmering with light, the next attack roll against it has Advantage. **")
        return True

# Create the instance
guiding_bolt = GuidingBolt()






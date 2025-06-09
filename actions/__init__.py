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

# File: actions/spell_actions.py
from .base_actions import Action

class CastSpellAction(Action):
    def __init__(self, spell):
        super().__init__(f"Cast {spell.name}")
        self.spell = spell

    def execute(self, performer, target=None, action_type="ACTION"):
        """Executes the spell cast, including spending the slot."""
        if performer.spell_slots.get(self.spell.level, 0) > 0:
            log_message = f"{action_type}: {performer.name} expends a level {self.spell.level} spell slot ({performer.spell_slots[self.spell.level]-1} remaining), to cast {self.spell.name} ({self.spell.school})"
            if "Ranged" in self.spell.attack_save or "Melee" in self.spell.attack_save:
                 if target:
                    log_message += f" at {target.name} (AC: {target.ac})."
            else:
                log_message += "."
            print(log_message)
            performer.spell_slots[self.spell.level] -= 1
            performer.cast_spell(self.spell, target, action_type)
        else:
            print(f"{action_type}: {performer.name} tries to cast {self.spell.name} but is out of level {self.spell.level} slots!")

# File: actions/special_actions.py
from .base_actions import Action

class LayOnHandsAction(Action):
    """Represents the Paladin's Lay on Hands ability."""
    def __init__(self):
        super().__init__("Lay on Hands")

    def execute(self, performer, target=None, action_type="BONUS ACTION"):
        target_to_heal = target or performer
        heal_amount = performer.get_optimal_lay_on_hands_amount(target_to_heal)
        performer.use_lay_on_hands(heal_amount, target_to_heal)

class MultiattackAction(Action):
    """An action that represents a creature's multiattack."""
    def __init__(self, creature):
        super().__init__(f"Multiattack")
        self.creature = creature

    def execute(self, performer, target, action_type="ACTION"):
        if hasattr(performer, 'multiattack'):
            performer.multiattack(target, action_type)
        else:
            # Fallback to regular attack
            performer.attack(target, action_type)

# File: spells/__init__.py
"""Magic system - spells organized by level and school."""

# Import commonly used spells
from .level_1.cure_wounds import cure_wounds
from .level_1.guiding_bolt import guiding_bolt
from .level_1.searing_smite import searing_smite

__all__ = ['cure_wounds', 'guiding_bolt', 'searing_smite']

# File: spells/level_1/__init__.py
"""1st level spells."""

from .cure_wounds import cure_wounds
from .guiding_bolt import guiding_bolt
from .searing_smite import searing_smite
from .heroism import heroism
from .bless import bless

__all__ = ['cure_wounds', 'guiding_bolt', 'searing_smite', 'heroism', 'bless']

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

# File: spells/level_1/searing_smite.py
from ..base_spell import Spell

class SearingSmite(Spell):
    def __init__(self):
        super().__init__(name="Searing Smite", level=1, school="Evocation", casting_time="1 Bonus Action",
                         requires_concentration=True, damage_type="Fire")

    def cast(self, caster, target=None):
        caster.active_smites.append(self)
        if self.requires_concentration:
            caster.start_concentrating(self)
        return True

# Create the instance
searing_smite = SearingSmite()

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
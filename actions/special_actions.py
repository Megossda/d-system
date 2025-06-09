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
# actions.py

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

class LayOnHandsAction(Action):
    """Represents the Paladin's Lay on Hands ability."""
    def __init__(self):
        super().__init__("Lay on Hands")

    def execute(self, performer, target=None, action_type="BONUS ACTION"):
        target_to_heal = target or performer
        performer.use_lay_on_hands(10, target_to_heal)

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

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
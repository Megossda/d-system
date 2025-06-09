from .base_actions import Action


class LayOnHandsAction(Action):
    """Represents the Paladin's Lay on Hands ability."""

    def __init__(self):  # FIXED: was def **init**
        super().__init__("Lay on Hands")

    def execute(self, performer, target=None, action_type="BONUS ACTION"):
        target_to_heal = target or performer
        heal_amount = performer.get_optimal_lay_on_hands_amount(target_to_heal)
        performer.use_lay_on_hands(heal_amount, target_to_heal)


class MultiattackAction(Action):
    """An action that represents a creature's multiattack."""

    def __init__(self, creature):  # FIXED: was def **init**
        super().__init__("Multiattack")
        self.creature = creature

    def execute(self, performer, target, action_type="ACTION"):
        if hasattr(performer, 'multiattack'):
            performer.multiattack(target, action_type)
        else:
            performer.attack(target, action_type)
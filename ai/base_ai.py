from actions.base_actions import AttackAction

class AIBrain:
    """A base class for character decision-making AI."""

    def choose_actions(self, character, combatants):
        """
        Determines the best action and bonus action for a character to take.
        Returns a dictionary with action, bonus_action, and targets.
        """
        action = AttackAction(character.equipped_weapon)
        bonus_action = None
        target = next((c for c in combatants if c.is_alive and c != character), None)

        return {
            'action': action,
            'bonus_action': bonus_action,
            'action_target': target,
            'bonus_action_target': None
        }
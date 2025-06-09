# File: ai/enemy_ai/humanoid_ai.py
from ..base_ai import AIBrain
from actions.base_actions import AttackAction

class HobgoblinWarriorAI(AIBrain):
    """AI for the Hobgoblin Warrior to choose between melee and ranged attacks."""

    def choose_actions(self, character, combatants):
        action = None
        target = next((c for c in combatants if c.is_alive and c != character), None)

        if target:
            distance = abs(character.position - target.position)
            # If target is far away, use the longbow
            if distance > 5 and character.secondary_weapon:
                action = AttackAction(character.secondary_weapon)
            # Otherwise, use the longsword
            else:
                action = AttackAction(character.equipped_weapon)
        else:
            action = AttackAction(character.equipped_weapon)

        return {'action': action, 'bonus_action': None, 'action_target': target}
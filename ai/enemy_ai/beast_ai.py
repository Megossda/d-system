# File: ai/enemy_ai/beast_ai.py
from ..base_ai import AIBrain
from actions.base_actions import AttackAction
from actions.special_actions import MultiattackAction

class GiantConstrictorSnakeAI(AIBrain):
    """AI for the Giant Constrictor Snake with multiattack and grappling tactics."""

    def choose_actions(self, character, combatants):
        action = None
        target = next((c for c in combatants if c.is_alive and c != character), None)

        if target:
            # If already grappling, keep using multiattack on the grappled target
            if hasattr(character, 'is_grappling') and character.is_grappling and hasattr(character, 'grapple_target') and character.grapple_target and character.grapple_target.is_alive:
                target = character.grapple_target
                print(f"[SNAKE AI] {character.name} continues grappling {target.name}")

            # Always prioritize multiattack for the snake
            action = MultiattackAction(character)
        else:
            action = AttackAction(character.equipped_weapon)

        return {'action': action, 'bonus_action': None, 'action_target': target}
# File: ai/enemy_ai/beast/giant_constrictor_snake_ai.py
from ...intelligence_based_ai import IntelligenceBasedAI
from actions.base_actions import AttackAction
from actions.special_actions import MultiattackAction
import random


class GiantConstrictorSnakeAI(IntelligenceBasedAI):
    """Giant Constrictor Snake AI - INT 1, pure predator instinct with optimal crushing tactics."""

    def instinctive_behavior(self, character, target):
        """Snake instincts: CRUSH grappled prey for guaranteed damage OR attempt new grapple."""
        distance = abs(character.position - target.position)
        
        # PRIORITY 1: If already grappling prey, CRUSH for guaranteed damage
        if hasattr(character, 'is_grappling') and character.is_grappling:
            if hasattr(character, 'grapple_target') and character.grapple_target and character.grapple_target.is_alive:
                grappled_target = character.grapple_target
                
                # OPTIMAL: Use dedicated crush action for guaranteed damage
                print(f"[SNAKE INSTINCT] {character.name} chooses to crush its grappled prey (guaranteed damage)")
                
                # CRITICAL: Mark this as a specialized decision that should NOT be overridden
                character._snake_ai_critical_decision = True
                character._snake_ai_decision_reason = "Optimal crush for guaranteed damage"
                
                return {
                    'action': 'crush_grappled_target',  # Special action for guaranteed damage
                    'bonus_action': None,
                    'action_target': grappled_target,
                    'bonus_action_target': None
                }
        
        # PRIORITY 2: Not grappling - try to grapple if in range
        if distance <= 10:
            print(f"[SNAKE INSTINCT] {character.name} attempts to grapple prey")
            return {
                'action': self._get_multiattack_action(character),
                'bonus_action': None,
                'action_target': target,
                'bonus_action_target': None
            }
        
        # PRIORITY 3: Too far away - move closer (handled by movement system)
        print(f"[SNAKE INSTINCT] {character.name} needs to get closer")
        return {
            'action': self._get_multiattack_action(character),  # Will move closer via movement system
            'bonus_action': None,
            'action_target': target,
            'bonus_action_target': None
        }

    def _get_multiattack_action(self, character):
        """Get or create multiattack action."""
        for action in character.available_actions:
            if isinstance(action, MultiattackAction):
                return action

        return MultiattackAction(character)
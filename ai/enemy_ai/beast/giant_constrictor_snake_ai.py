# File: ai/enemy_ai/beast/giant_constrictor_snake_ai.py
from ...intelligence_based_ai import IntelligenceBasedAI
from actions.base_actions import AttackAction
from actions.special_actions import MultiattackAction
import random


class GiantConstrictorSnakeAI(IntelligenceBasedAI):
    """Giant Constrictor Snake AI - INT 1, pure predator instinct."""

    def enhance_ai_brain_with_range_analysis(ai_brain, range_manager):
        """Enhance existing AI brain with range-based tactical analysis"""
        
        # NEW: Don't override specialized AI that handles multiattack
        from ai.enemy_ai.beast.giant_constrictor_snake_ai import GiantConstrictorSnakeAI
        if isinstance(ai_brain, GiantConstrictorSnakeAI):
            print(f"[TACTICAL AI] Skipping range analysis for specialized multiattack AI")
            return ai_brain  # Return unchanged
        
        original_choose_actions = ai_brain.choose_actions

        def enhanced_choose_actions(character, combatants):
            # Rest of the function stays the same...
            original_decision = original_choose_actions(character, combatants)
            target = original_decision.get('action_target')
            if not target:
                return original_decision

            recommendations = range_manager.get_tactical_recommendations(character, target)

            if recommendations['best_option']:
                best = recommendations['best_option']
                print(f"[TACTICAL AI] {character.name} analyzing options:")
                print(f"  Current distance to {target.name}: {recommendations['current_distance']}ft")
                print(f"  Best option: {best['action_description']} (Priority: {best['priority']:.1f})")

                if best['type'] == 'weapon':
                    from actions import AttackAction
                    original_decision['action'] = AttackAction(best['weapon'])
                elif best['type'] == 'spell':
                    from actions import CastSpellAction
                    original_decision['action'] = CastSpellAction(best['spell'])

            return original_decision

        ai_brain.choose_actions = enhanced_choose_actions
        return ai_brain
    
    def instinctive_behavior(self, character, target):
        """Snake instincts: crush grappled prey OR attempt new grapple."""
        distance = abs(character.position - target.position)
        
        # If already grappling prey, CRUSH for guaranteed damage
        if hasattr(character, 'is_grappling') and character.is_grappling:
            if hasattr(character, 'grapple_target') and character.grapple_target and character.grapple_target.is_alive:
                grappled_target = character.grapple_target
                
                # ALWAYS crush for guaranteed damage vs high AC targets
                print(f"[SNAKE INSTINCT] {character.name} chooses to crush its grappled prey (guaranteed damage)")
                return {
                    'action': 'crush_grappled_target',  # Special action type
                    'bonus_action': None,
                    'action_target': grappled_target,
                    'bonus_action_target': None
                }
        
        # Not grappling - try to grapple
        if distance <= 10:
            print(f"[SNAKE INSTINCT] {character.name} attempts to grapple prey")
            return {
                'action': self._get_multiattack_action(character),
                'bonus_action': None,
                'action_target': target,
                'bonus_action_target': None
            }
        
        # Too far away
        print(f"[SNAKE INSTINCT] {character.name} needs to get closer")
        return {
            'action': AttackAction(character.equipped_weapon),
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
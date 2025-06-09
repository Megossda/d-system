# File: ai/enemy_ai/humanoid/hobgoblin_warrior_ai.py
from ...intelligence_based_ai import IntelligenceBasedAI
from actions.base_actions import AttackAction


class HobgoblinWarriorAI(IntelligenceBasedAI):
    """Hobgoblin Warrior AI - INT 10, basic military tactics."""

    def basic_strategy(self, character, enemies, all_combatants):
        """Hobgoblin uses basic military tactics - range vs melee decisions."""
        target = self.select_tactical_target(character, enemies)
        if not target:
            return self.default_action_set(character)

        distance = abs(character.position - target.position)

        # Strategic weapon choice based on range and tactical situation
        action = self._choose_weapon_strategically(character, target, distance)

        return {
            'action': action,
            'bonus_action': None,
            'action_target': target,
            'bonus_action_target': None
        }

    def tactical_behavior(self, character, target, enemies):
        """Simple tactical weapon switching."""
        distance = abs(character.position - target.position)
        action = self._choose_weapon_tactically(character, target, distance)

        return {
            'action': action,
            'bonus_action': None,
            'action_target': target,
            'bonus_action_target': None
        }

    def _choose_weapon_strategically(self, character, target, distance):
        """Strategic weapon choice considering multiple factors."""
        # Consider our health
        our_hp_percent = character.hp / character.max_hp
        target_hp_percent = target.hp / target.max_hp

        # If we're badly wounded, prefer ranged combat
        if our_hp_percent < 0.3 and character.secondary_weapon and distance > 5:
            print(f"[HOBGOBLIN STRATEGY] Wounded, using ranged combat")
            return AttackAction(character.secondary_weapon)

        # If target is nearly dead, close in for the kill
        if target_hp_percent < 0.3 and distance > 5:
            print(f"[HOBGOBLIN STRATEGY] Target wounded, closing for melee")
            return AttackAction(character.equipped_weapon)

        # Default to tactical choice
        return self._choose_weapon_tactically(character, target, distance)

    def _choose_weapon_tactically(self, character, target, distance):
        """Basic tactical weapon choice based on range."""
        # Use ranged weapon if target is far and we have one
        if distance > 5 and character.secondary_weapon:
            print(f"[HOBGOBLIN TACTICS] Using ranged weapon at {distance}ft")
            return AttackAction(character.secondary_weapon)
        else:
            print(f"[HOBGOBLIN TACTICS] Using melee weapon")
            return AttackAction(character.equipped_weapon)
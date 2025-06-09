# File: ai/enemy_ai/humanoid/goblin_ai.py
from ...intelligence_based_ai import IntelligenceBasedAI
from actions.base_actions import AttackAction
import random


class GoblinAI(IntelligenceBasedAI):
    """Goblin AI - INT 10, but cowardly and erratic behavior."""

    def basic_strategy(self, character, enemies, all_combatants):
        """Goblins are smart but cowardly - prone to panic."""
        target = self.select_tactical_target(character, enemies)
        if not target:
            return self.default_action_set(character)

        # Check for cowardice
        if self._should_panic(character, enemies):
            return self._panic_behavior(character, target)

        # Otherwise use simple tactics
        return self.tactical_behavior(character, target, enemies)

    def tactical_behavior(self, character, target, enemies):
        """Simple goblin tactics - opportunistic and sneaky."""
        distance = abs(character.position - target.position)

        # Goblins prefer to attack when they have advantage
        if self._has_tactical_advantage(character, target, enemies):
            print(f"[GOBLIN TACTICS] Sees opportunity, attacking aggressively")
            return {
                'action': AttackAction(character.equipped_weapon),
                'bonus_action': None,
                'action_target': target,
                'bonus_action_target': None
            }
        else:
            print(f"[GOBLIN TACTICS] Cautious attack")
            return {
                'action': AttackAction(character.equipped_weapon),
                'bonus_action': None,
                'action_target': target,
                'bonus_action_target': None
            }

    def _should_panic(self, character, enemies):
        """Check if goblin should panic based on situation."""
        our_hp_percent = character.hp / character.max_hp

        # Panic if badly wounded
        if our_hp_percent < 0.25:
            return random.random() < 0.7  # 70% chance to panic when low HP

        # Panic if outnumbered (in future multi-enemy scenarios)
        # For now, just occasional random panic
        return random.random() < 0.1  # 10% chance of random panic

    def _panic_behavior(self, character, target):
        """Panicked goblin behavior - still attacks but erratically."""
        print(f"[GOBLIN PANIC] {character.name} is panicking but still fighting!")

        # Panicked goblins attack wildly
        return {
            'action': AttackAction(character.equipped_weapon),
            'bonus_action': None,
            'action_target': target,
            'bonus_action_target': None
        }

    def _has_tactical_advantage(self, character, target, enemies):
        """Simple check for tactical advantage."""
        our_hp_percent = character.hp / character.max_hp
        target_hp_percent = target.hp / target.max_hp

        # Feel brave if we're healthy and target is wounded
        return our_hp_percent > 0.7 and target_hp_percent < 0.5
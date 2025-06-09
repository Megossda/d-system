# File: ai/intelligence_based_ai.py
from .base_ai import AIBrain
from actions.base_actions import AttackAction
from actions.special_actions import MultiattackAction
import random


class IntelligenceBasedAI(AIBrain):
    """Base class that adapts AI behavior based on creature intelligence."""

    def __init__(self):
        super().__init__()
        self.intelligence_tier = None

    def choose_actions(self, character, combatants):
        """Route to appropriate intelligence tier."""
        intelligence = character.stats.get('int', 10)

        if intelligence <= 3:
            return self.bestial_instinct(character, combatants)
        elif intelligence <= 7:
            return self.simple_tactics(character, combatants)
        elif intelligence <= 12:
            return self.basic_strategy(character, combatants)
        else:
            return self.complex_planning(character, combatants)

    def bestial_instinct(self, character, combatants):
        """INT 1-3: Pure animal instinct - attack closest, constrict when possible."""
        target = self.get_closest_enemy(character, combatants)
        if not target:
            return self.default_action_set(character)

        print(f"[BESTIAL INSTINCT] {character.name} acts on pure predator instinct")

        # Simple behavior: attack what's closest, use abilities when in range
        return self.instinctive_behavior(character, target)

    def simple_tactics(self, character, combatants):
        """INT 4-7: Basic tactical awareness - positioning, target selection."""
        enemies = [c for c in combatants if c.is_alive and c != character]
        if not enemies:
            return self.default_action_set(character)

        print(f"[SIMPLE TACTICS] {character.name} uses basic tactical thinking")

        # Choose target based on simple criteria: wounded, close, weak
        target = self.select_tactical_target(character, enemies)
        return self.tactical_behavior(character, target, enemies)

    def basic_strategy(self, character, combatants):
        """INT 8-12: Strategic thinking - considers outcomes, team coordination."""
        enemies = [c for c in combatants if c.is_alive and c != character]
        if not enemies:
            return self.default_action_set(character)

        print(f"[BASIC STRATEGY] {character.name} thinks strategically")

        # Evaluate multiple factors and plan ahead
        return self.strategic_behavior(character, enemies, combatants)

    def complex_planning(self, character, combatants):
        """INT 13+: Advanced planning - predicts opponent moves, complex tactics."""
        enemies = [c for c in combatants if c.is_alive and c != character]
        if not enemies:
            return self.default_action_set(character)

        print(f"[COMPLEX PLANNING] {character.name} employs advanced tactics")

        # Deep analysis of battlefield state and opponent capabilities
        return self.advanced_behavior(character, enemies, combatants)

    # Helper methods to be overridden by specific creature AIs
    def instinctive_behavior(self, character, target):
        """Override this for specific creature instincts."""
        return {
            'action': AttackAction(character.equipped_weapon),
            'bonus_action': None,
            'action_target': target,
            'bonus_action_target': None
        }

    def tactical_behavior(self, character, target, enemies):
        """Override this for creature-specific tactics."""
        return self.instinctive_behavior(character, target)

    def strategic_behavior(self, character, enemies, all_combatants):
        """Override this for creature-specific strategy."""
        target = enemies[0] if enemies else None
        return self.tactical_behavior(character, target, enemies)

    def advanced_behavior(self, character, enemies, all_combatants):
        """Override this for creature-specific advanced planning."""
        return self.strategic_behavior(character, enemies, all_combatants)

    # Utility methods
    def get_closest_enemy(self, character, combatants):
        """Find the closest living enemy."""
        enemies = [c for c in combatants if c.is_alive and c != character]
        if not enemies:
            return None

        return min(enemies, key=lambda e: abs(character.position - e.position))

    def select_tactical_target(self, character, enemies):
        """Basic target selection: prioritize wounded or weak targets."""
        # Prefer wounded targets
        wounded = [e for e in enemies if e.hp < e.max_hp * 0.5]
        if wounded:
            return min(wounded, key=lambda e: e.hp / e.max_hp)

        # Otherwise, closest target
        return min(enemies, key=lambda e: abs(character.position - e.position))

    def default_action_set(self, character):
        """Default action when no valid targets."""
        return {
            'action': AttackAction(character.equipped_weapon),
            'bonus_action': None,
            'action_target': None,
            'bonus_action_target': None
        }
# File: ai/enemy_ai/beast/giant_octopus_ai.py
from ...intelligence_based_ai import IntelligenceBasedAI
from actions.base_actions import AttackAction
import random


class GiantOctopusAI(IntelligenceBasedAI):
    """Giant Octopus AI - INT 5, basic predator tactics with multi-grappling strategy."""

    def simple_tactics(self, character, enemies):
        """Giant Octopus uses basic tactical thinking - grapple multiple targets."""
        target = self.select_tactical_target(character, enemies)
        if not target:
            return self.default_action_set(character)

        distance = abs(character.position - target.position)

        print(f"[OCTOPUS TACTICS] {character.name} analyzing multi-grapple strategy")

        # Priority 1: If we can grapple more targets, try to grapple
        if character.can_grapple_more_targets() and distance <= 10:
            print(f"[OCTOPUS TACTICS] Attempting to grapple new target ({len(character.grappled_targets)}/{character.max_tentacles} tentacles used)")
            return {
                'action': 'tentacle_attack',  # Special action
                'bonus_action': None,
                'action_target': target,
                'bonus_action_target': None
            }

        # Priority 2: If we have grappled targets, squeeze them all
        elif character.grappled_targets:
            valid_targets = [t for t in character.grappled_targets if t and t.is_alive]
            if valid_targets:
                print(f"[OCTOPUS TACTICS] Squeezing {len(valid_targets)} grappled targets")
                return {
                    'action': 'squeeze_grappled_targets',  # Special action
                    'bonus_action': None,
                    'action_target': None,  # Targets all grappled creatures
                    'bonus_action_target': None
                }

        # Priority 3: Regular attack if can't grapple and no grappled targets
        print(f"[OCTOPUS TACTICS] Using standard tentacle attack")
        return {
            'action': AttackAction(character.equipped_weapon),
            'bonus_action': None,
            'action_target': target,
            'bonus_action_target': None
        }

    def select_tactical_target(self, character, enemies):
        """Select best target for octopus - prefer ungrappled, smaller targets."""
        # Filter out already grappled targets
        ungrappled_enemies = []
        grappled_enemies = []
        
        for enemy in enemies:
            if hasattr(enemy, 'is_grappled') and enemy.is_grappled and enemy in character.grappled_targets:
                grappled_enemies.append(enemy)
            else:
                ungrappled_enemies.append(enemy)

        # Prefer ungrappled targets if we can grapple more
        if ungrappled_enemies and character.can_grapple_more_targets():
            # Prefer smaller targets (easier to grapple)
            small_targets = [e for e in ungrappled_enemies if getattr(e, 'size', 'Medium') in ['Tiny', 'Small', 'Medium']]
            if small_targets:
                return min(small_targets, key=lambda e: abs(character.position - e.position))
            else:
                return min(ungrappled_enemies, key=lambda e: abs(character.position - e.position))

        # Otherwise, closest enemy
        all_enemies = ungrappled_enemies + grappled_enemies
        if all_enemies:
            return min(all_enemies, key=lambda e: abs(character.position - e.position))

        return None
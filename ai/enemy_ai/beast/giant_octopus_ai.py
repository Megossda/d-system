# File: ai/enemy_ai/beast/giant_octopus_ai.py
from ...intelligence_based_ai import IntelligenceBasedAI
from actions.base_actions import AttackAction
import random


class GiantOctopusAI(IntelligenceBasedAI):
    """Giant Octopus AI - INT 4, basic predator tactics focusing on single-target grappling."""

    def simple_tactics(self, character, enemies):
        """Giant Octopus uses basic tactical thinking - grapple one target with all tentacles."""
        target = self.select_tactical_target(character, enemies)
        if not target:
            return self.default_action_set(character)

        distance = abs(character.position - target.position)

        print(f"[OCTOPUS TACTICS] {character.name} analyzing grappling strategy")

        # PHB 2024: Octopus can only grapple ONE creature with its Tentacles action
        # Priority 1: If not grappling anyone, try to grapple
        if not character.is_grappling and distance <= 10:
            print(f"[OCTOPUS TACTICS] Attempting to grapple target with all tentacles")
            return {
                'action': 'tentacle_attack',  # Special action
                'bonus_action': None,
                'action_target': target,
                'bonus_action_target': None
            }

        # Priority 2: If already grappling, attack the same target again (PHB 2024)
        elif character.is_grappling and character.grappled_target and character.grappled_target.is_alive:
            grappled_target = character.grappled_target
            print(f"[OCTOPUS TACTICS] Already grappling {grappled_target.name}, attacking again with Tentacles")
            print(f"[OCTOPUS TACTICS] Target is Restrained - attack will have Advantage")
            return {
                'action': 'tentacle_attack',  # Only action available - attack the grappled target
                'bonus_action': None,
                'action_target': grappled_target,  # Must target the grappled creature
                'bonus_action_target': None
            }

        # Priority 3: If grappling invalid target, try to grapple new target
        elif character.is_grappling and (not character.grappled_target or not character.grappled_target.is_alive):
            print(f"[OCTOPUS TACTICS] Grappled target invalid, seeking new target")
            character.is_grappling = False  # Clean up invalid state
            character.grappled_target = None
            return {
                'action': 'tentacle_attack',
                'bonus_action': None,
                'action_target': target,
                'bonus_action_target': None
            }

        # Priority 4: Target too far away, still try to attack (will move closer first)
        print(f"[OCTOPUS TACTICS] Target at {distance}ft, will move closer and attack")
        return {
            'action': 'tentacle_attack',
            'bonus_action': None,
            'action_target': target,
            'bonus_action_target': None
        }

    def select_tactical_target(self, character, enemies):
        """Select best target for octopus - prefer ungrappled, smaller targets."""
        if not enemies:
            return None
            
        # If already grappling, prioritize the grappled target
        if character.is_grappling and character.grappled_target and character.grappled_target.is_alive:
            if character.grappled_target in enemies:
                return character.grappled_target
        
        # Filter out targets that are too large to grapple
        grappable_enemies = []
        for enemy in enemies:
            enemy_size = getattr(enemy, 'size', 'Medium')
            if enemy_size in ['Tiny', 'Small', 'Medium']:
                grappable_enemies.append(enemy)
        
        if not grappable_enemies:
            # No grappable targets, just attack closest
            return min(enemies, key=lambda e: abs(character.position - e.position))
        
        # Prefer closest grappable target
        return min(grappable_enemies, key=lambda e: abs(character.position - e.position))
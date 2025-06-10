# range_manager.py

from typing import Dict, List, Tuple, Optional
import math
from actions.base_actions import AttackAction  # ADD THIS LINE


class WeaponRanges:
    """Centralized weapon range definitions in feet"""

    # Standard D&D 5e weapon ranges
    WEAPON_RANGES = {
        # Melee weapons (5ft reach)
        'club': 5,
        'dagger': 5,
        'handaxe': 5,
        'javelin': 5,  # When used in melee
        'light_hammer': 5,
        'mace': 5,
        'quarterstaff': 5,
        'sickle': 5,
        'spear': 5,  # When used in melee
        'battleaxe': 5,
        'flail': 5,
        'longsword': 5,  # As you specified
        'morningstar': 5,
        'rapier': 5,
        'scimitar': 5,
        'shortsword': 5,
        'trident': 5,  # When used in melee
        'war_pick': 5,
        'warhammer': 5,

        # Reach weapons (10ft)
        'glaive': 10,
        'halberd': 10,
        'lance': 10,
        'pike': 10,
        'whip': 10,

        # Two-handed melee (5ft)
        'greataxe': 5,
        'greatsword': 5,
        'maul': 5,
        'greatclub': 5,

        # Thrown weapons (when thrown)
        'dart': 20,
        'javelin_thrown': 30,
        'handaxe_thrown': 20,
        'light_hammer_thrown': 20,
        'spear_thrown': 20,
        'trident_thrown': 20,

        # Ranged weapons
        'shortbow': 80,
        'longbow': 150,
        'light_crossbow': 80,
        'heavy_crossbow': 100,
        'hand_crossbow': 30,
        'sling': 30,
        'blowgun': 25,

        # Special cases from your enemies.py
        'hobgoblin_longsword': 5,
        'poisoned_longbow': 150,

        # Spells (rough estimates)
        'fire_bolt': 120,
        'guiding_bolt': 120,
        'cure_wounds': 5,  # Touch spell
        'searing_smite': 5,  # Applied to melee attacks
    }

    @classmethod
    def get_weapon_range(cls, weapon):
        """Get the range of a weapon in feet"""
        # Check if it's a weapon object (duck typing instead of isinstance)
        if hasattr(weapon, 'name') and hasattr(weapon, 'properties'):
            weapon_name = weapon.name.lower().replace(' ', '_').replace("'", '').replace('+1_', '')

            # Check for ranged property first
            if hasattr(weapon, 'properties') and 'Ranged' in weapon.properties:
                # Special handling for specific ranged weapons
                if 'longbow' in weapon_name or 'poisoned_longbow' in weapon_name:
                    return 150
                elif 'shortbow' in weapon_name:
                    return 80
                elif 'crossbow' in weapon_name:
                    if 'heavy' in weapon_name:
                        return 100
                    elif 'hand' in weapon_name:
                        return 30
                    else:  # light crossbow
                        return 80
                else:
                    return 60  # Default ranged weapon range

            # Check our range database
            return cls.WEAPON_RANGES.get(weapon_name, 5)  # Default to 5ft

        # If it's just a string
        weapon_name = str(weapon).lower().replace(' ', '_')
        return cls.WEAPON_RANGES.get(weapon_name, 5)

    @classmethod
    def is_ranged_weapon(cls, weapon):
        """Check if a weapon is ranged"""
        if hasattr(weapon, 'properties'):
            return hasattr(weapon, 'properties') and 'Ranged' in weapon.properties
        return False

    @classmethod
    def is_reach_weapon(cls, weapon):
        """Check if a weapon has reach"""
        if hasattr(weapon, 'properties'):
            return hasattr(weapon, 'properties') and 'Reach' in weapon.properties
        return cls.get_weapon_range(weapon) == 10


class CombatRangeManager:
    """Manages range calculations and tactical positioning for combat"""

    def __init__(self):
        self.combatants = []
        self.distance_matrix = {}

    def initialize_combat(self, combatants):
        """Initialize the range system with current combatant positions"""
        self.combatants = combatants
        self._calculate_all_distances()

        print("\n--- COMBAT RANGE INITIALIZATION ---")
        for combatant in combatants:
            weapons_info = self._get_combatant_weapons_info(combatant)
            print(f"{combatant.name} at position {combatant.position}ft:")
            for weapon_name, weapon_range in weapons_info.items():
                weapon_type = "Ranged" if WeaponRanges.is_ranged_weapon(
                    getattr(combatant, 'equipped_weapon', None)) or WeaponRanges.is_ranged_weapon(
                    getattr(combatant, 'secondary_weapon', None)) else "Melee"
                if weapon_name.lower() in ['equipped_weapon', 'secondary_weapon']:
                    weapon_obj = getattr(combatant, weapon_name, None)
                    if weapon_obj:
                        weapon_type = "Ranged" if WeaponRanges.is_ranged_weapon(weapon_obj) else "Melee"
                        print(f"  - {weapon_obj.name}: {weapon_range}ft ({weapon_type})")

        self._print_initial_distances()

    def _get_combatant_weapons_info(self, combatant):
        """Get all weapons and their ranges for a combatant"""
        weapons_info = {}

        if hasattr(combatant, 'equipped_weapon') and combatant.equipped_weapon:
            weapons_info['equipped_weapon'] = WeaponRanges.get_weapon_range(combatant.equipped_weapon)

        if hasattr(combatant, 'secondary_weapon') and combatant.secondary_weapon:
            weapons_info['secondary_weapon'] = WeaponRanges.get_weapon_range(combatant.secondary_weapon)

        return weapons_info

    def _calculate_all_distances(self):
        """Calculate distances between all combatants"""
        self.distance_matrix = {}

        for i, combatant1 in enumerate(self.combatants):
            for j, combatant2 in enumerate(self.combatants):
                if i != j:
                    distance = abs(combatant1.position - combatant2.position)
                    self.distance_matrix[(combatant1.name, combatant2.name)] = distance

    def _print_initial_distances(self):
        """Print the initial distances between combatants"""
        print("\n--- INITIAL DISTANCES ---")
        processed_pairs = set()

        for (name1, name2), distance in self.distance_matrix.items():
            pair = tuple(sorted([name1, name2]))
            if pair not in processed_pairs:
                processed_pairs.add(pair)
                print(f"{name1} <-> {name2}: {distance}ft")

    def get_distance_between(self, combatant1, combatant2):
        """Get distance between two combatants"""
        if isinstance(combatant1, str):
            name1 = combatant1
        else:
            name1 = combatant1.name

        if isinstance(combatant2, str):
            name2 = combatant2
        else:
            name2 = combatant2.name

        return self.distance_matrix.get((name1, name2), abs(combatant1.position - combatant2.position))

    def get_tactical_recommendations(self, attacker, target):
        """Get AI recommendations for the best tactical approach"""
        current_distance = self.get_distance_between(attacker, target)
        recommendations = []

        # Analyze multiattack actions first (highest priority for creatures that have them)
        if hasattr(attacker, 'available_actions'):
            from actions.special_actions import MultiattackAction
            for action in attacker.available_actions:
                if isinstance(action, MultiattackAction):
                    multiattack_rec = self._analyze_multiattack_option(attacker, target, action, current_distance)
                    if multiattack_rec:
                        recommendations.append(multiattack_rec)

        # Analyze primary weapon
        if hasattr(attacker, 'equipped_weapon') and attacker.equipped_weapon:
            rec = self._analyze_weapon_option(attacker, target, attacker.equipped_weapon, current_distance, "primary")
            recommendations.append(rec)

        # Analyze secondary weapon
        if hasattr(attacker, 'secondary_weapon') and attacker.secondary_weapon:
            rec = self._analyze_weapon_option(attacker, target, attacker.secondary_weapon, current_distance,
                                              "secondary")
            recommendations.append(rec)

        # Analyze spells if available
        if hasattr(attacker, 'prepared_spells'):
            for spell in attacker.prepared_spells:
                if hasattr(attacker, 'spell_slots') and attacker.spell_slots.get(spell.level, 0) > 0:
                    # Check if we can cast this spell (2024 rule: only one spell slot per turn)
                    # If we already chose a bonus action spell that uses a slot, we can't cast another
                    can_cast_spell = True
                    for existing_rec in recommendations:
                        if (existing_rec.get('type') == 'spell' and
                                hasattr(existing_rec.get('spell'), 'level') and
                                existing_rec.get('spell').level > 0):
                            can_cast_spell = False
                            break

                    if can_cast_spell:
                        rec = self._analyze_spell_option(attacker, target, spell, current_distance)
                        if rec:
                            recommendations.append(rec)

        # Sort by priority
        recommendations.sort(key=lambda x: x['priority'], reverse=True)

        return {
            'current_distance': current_distance,
            'recommendations': recommendations,
            'best_option': recommendations[0] if recommendations else None
        }

    def _analyze_multiattack_option(self, attacker, target, multiattack_action, current_distance):
        """Analyze a multiattack action option."""
        # Multiattack is typically melee-based
        is_in_range = current_distance <= 5  # Most multiattacks require melee range
        movement_needed = 0
        can_reach_this_turn = True
        
        if not is_in_range:
            movement_needed = current_distance - 5
            attacker_speed = getattr(attacker, 'speed', 30)
            can_reach_this_turn = movement_needed <= attacker_speed
        
        # Calculate priority - multiattack should be VERY high priority
        priority = 40.0  # Base high priority for multiattack
        
        if is_in_range:
            priority += 15  # Big bonus for being in range
            action_description = "Use Multiattack"
        elif can_reach_this_turn:
            priority += 10  # Good bonus for reachable multiattack
            action_description = f"Move {movement_needed}ft and use Multiattack"
        else:
            priority -= 20  # Penalty for unreachable
            action_description = f"Move toward target for future Multiattack"
        
        # Special bonus for creatures designed around multiattack (like snakes)
        if hasattr(attacker, 'is_grappling') or 'Snake' in attacker.name:
            priority += 10  # Extra priority for grappling creatures
        
        return {
            'type': 'multiattack',
            'action': multiattack_action,
            'is_in_range': is_in_range,
            'movement_needed': movement_needed,
            'can_reach_this_turn': can_reach_this_turn,
            'action_description': action_description,
            'priority': priority
        }

    def _analyze_weapon_option(self, attacker, target, weapon, current_distance, weapon_type):
        """Analyze a specific weapon option"""
        weapon_range = WeaponRanges.get_weapon_range(weapon)
        is_ranged = WeaponRanges.is_ranged_weapon(weapon)
        is_in_range = current_distance <= weapon_range

        # Calculate movement needed
        movement_needed = 0
        action_description = ""
        can_reach_this_turn = True

        if is_in_range:
            action_description = f"Attack with {weapon.name}"
            movement_needed = 0
        else:
            if is_ranged:
                # For ranged weapons, we don't usually need to move closer
                action_description = f"Move into range and attack with {weapon.name}"
                movement_needed = max(0, current_distance - weapon_range)
            else:
                # For melee weapons, move to get in range
                movement_needed = current_distance - weapon_range
                
                # Check if we can actually reach with available movement
                attacker_speed = getattr(attacker, 'speed', 30)
                if movement_needed <= attacker_speed:
                    action_description = f"Move {movement_needed}ft and attack with {weapon.name}"
                else:
                    action_description = f"Move {attacker_speed}ft toward target (still {movement_needed - attacker_speed}ft away)"
                    can_reach_this_turn = False

        # Calculate priority score
        priority = self._calculate_weapon_priority(weapon, is_in_range, movement_needed, is_ranged, current_distance)
        
        # Heavily penalize options that can't reach target this turn
        if not can_reach_this_turn:
            priority -= 50  # Major penalty for unreachable targets

        return {
            'type': 'weapon',
            'weapon': weapon,
            'weapon_type': weapon_type,
            'weapon_range': weapon_range,
            'is_ranged': is_ranged,
            'is_in_range': is_in_range,
            'movement_needed': movement_needed,
            'can_reach_this_turn': can_reach_this_turn,
            'action_description': action_description,
            'priority': priority
        }

    def _analyze_spell_option(self, attacker, target, spell, current_distance):
        """Analyze a spell casting option"""
        spell_range = WeaponRanges.get_weapon_range(spell.name)
        is_in_range = current_distance <= spell_range

        if not is_in_range:
            return None  # Can't cast if out of range

        # Touch spells need to be in melee range
        if spell_range <= 5 and current_distance > 5:
            movement_needed = current_distance - 5
            action_description = f"Move {movement_needed}ft and cast {spell.name}"
        else:
            movement_needed = 0
            action_description = f"Cast {spell.name}"

        priority = self._calculate_spell_priority(spell, is_in_range, movement_needed)

        return {
            'type': 'spell',
            'spell': spell,
            'spell_range': spell_range,
            'is_in_range': is_in_range,
            'movement_needed': movement_needed,
            'action_description': action_description,
            'priority': priority
        }

    def _calculate_weapon_priority(self, weapon, is_in_range, movement_needed, is_ranged, current_distance):
        """Calculate priority score for a weapon choice"""
        priority = 5  # Base priority

        # Bonus for being in range
        if is_in_range:
            priority += 10

        # Penalty for movement needed
        priority -= movement_needed * 0.1

        # Prefer ranged when far away (>10ft)
        if is_ranged and current_distance > 10:
            priority += 5

        # Strongly prefer melee when close (<=10ft) and prefer ranged when far
        if not is_ranged and current_distance <= 10:
            priority += 8  # Increased from 3 to 8
        elif is_ranged and current_distance <= 10:
            priority -= 5  # Penalty for using ranged when close

        # Damage bonus (rough estimate based on weapon dice)
        if hasattr(weapon, 'damage_dice'):
            if '1d8' in weapon.damage_dice:
                priority += 2
            elif '1d10' in weapon.damage_dice or '2d6' in weapon.damage_dice:
                priority += 3
            elif '1d12' in weapon.damage_dice or '2d10' in weapon.damage_dice:
                priority += 4

        return priority

    def _calculate_spell_priority(self, spell, is_in_range, movement_needed):
        """Calculate priority score for a spell choice"""
        priority = 8  # Base priority for spells

        if is_in_range:
            priority += 10

        priority -= movement_needed * 0.1

        # Bonus for damage spells
        if hasattr(spell, 'damage_type') and spell.damage_type:
            priority += 5

        return priority

    def update_positions(self, combatants):
        """Update the distance matrix after movement"""
        self.combatants = combatants
        self._calculate_all_distances()

    def can_attack_with_weapon(self, attacker, target, weapon):
        """Check if attacker can attack target with given weapon"""
        current_distance = self.get_distance_between(attacker, target)
        weapon_range = WeaponRanges.get_weapon_range(weapon)
        return current_distance <= weapon_range

    def get_optimal_position(self, attacker, target, weapon):
        """Get the optimal position for using a weapon against a target"""
        weapon_range = WeaponRanges.get_weapon_range(weapon)
        is_ranged = WeaponRanges.is_ranged_weapon(weapon)

        if is_ranged:
            # For ranged weapons, stay at about 70% of maximum range
            optimal_distance = weapon_range * 0.7
            if target.position > attacker.position:
                return target.position - optimal_distance
            else:
                return target.position + optimal_distance
        else:
            # For melee weapons, get as close as possible
            if target.position > attacker.position:
                return target.position - 5
            else:
                return target.position + 5


# Integration function for existing AI brains
def enhance_ai_brain_with_range_analysis(ai_brain, range_manager):
    """Enhance existing AI brain with range-based tactical analysis"""
    original_choose_actions = ai_brain.choose_actions

    def enhanced_choose_actions(character, combatants):
        # Get the original decision
        original_decision = original_choose_actions(character, combatants)

        # FIXED: Check if specialized AI made a critical decision that shouldn't be overridden
        if hasattr(character, '_ai_has_made_critical_decision') and character._ai_has_made_critical_decision:
            reason = getattr(character, '_critical_decision_reason', 'Critical AI decision')
            print(f"[TACTICAL AI] {character.name}: Respecting specialized AI decision - {reason}")
            # Clear the flag for next turn
            character._ai_has_made_critical_decision = False
            if hasattr(character, '_critical_decision_reason'):
                delattr(character, '_critical_decision_reason')
            return original_decision

        # Handle case where AI returns None
        if original_decision is None:
            from actions.base_actions import AttackAction  # Import here temporarily
            return {
                'action': AttackAction(character.equipped_weapon),
                'bonus_action': None,
                'action_target': next((c for c in combatants if c.is_alive and c != character), None),
                'bonus_action_target': None
            }

        # Find target
        target = original_decision.get('action_target')
        if not target:
            return original_decision

        # Get tactical recommendations
        recommendations = range_manager.get_tactical_recommendations(character, target)

        # If we have a better option, use it
        if recommendations['best_option']:
            best = recommendations['best_option']

            print(f"[TACTICAL AI] {character.name} analyzing options:")
            print(f"  Current distance to {target.name}: {recommendations['current_distance']}ft")
            print(f"  Best option: {best['action_description']} (Priority: {best['priority']:.1f})")

            # Only use tactical recommendation if it's actually good
            if best['priority'] < 0:
                print(f"  Tactical option not viable, using original AI decision")
                return original_decision

            # Store tactical recommendation for movement execution
            character.ai_brain.last_tactical_recommendation = best

            # Update the action based on best recommendation
            if best['type'] == 'weapon':
                from actions import AttackAction
                original_decision['action'] = AttackAction(best['weapon'])
            elif best['type'] == 'spell':
                from actions import CastSpellAction
                original_decision['action'] = CastSpellAction(best['spell'])
            elif best['type'] == 'multiattack':
                # Properly handle multiattack recommendations
                original_decision['action'] = best['action']

        return original_decision

    ai_brain.choose_actions = enhanced_choose_actions
    return ai_brain


# Example usage with your existing code
def initialize_combat_with_ranges(combatants):
    """Initialize combat with range analysis"""
    range_manager = CombatRangeManager()
    range_manager.initialize_combat(combatants)

    # Enhance AI brains with range analysis
    for combatant in combatants:
        if hasattr(combatant, 'ai_brain'):
            combatant.ai_brain = enhance_ai_brain_with_range_analysis(combatant.ai_brain, range_manager)

    return range_manager
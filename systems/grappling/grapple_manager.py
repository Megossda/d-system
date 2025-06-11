# File: systems/grappling/grapple_manager.py
"""
Global Grappling Manager - Coordinates all grappling operations across the entire game.
This is the central hub that all creatures use for grappling interactions.
"""

from .universal_grapple import UniversalGrappling
from .grapple_conditions import GrappleConditionManager
from .grapple_actions import UniversalGrappleActions
from core import get_ability_modifier


class GlobalGrappleManager:
    """
    Central manager for all grappling operations in the game.
    Provides standardized interface for any creature to perform grappling actions.
    """
    
    @staticmethod
    def create_creature_grapple_attack(creature, damage_dice=None, attack_name=None, 
                                     damage_type="Bludgeoning", range_ft=5, method="attack"):
        """
        Create a standardized grapple attack for any creature.
        
        Args:
            creature: The creature that will use this attack
            damage_dice: Damage dice (auto-calculated if None)
            attack_name: Name of attack (auto-generated if None)
            damage_type: Type of damage
            range_ft: Range in feet
            method: "attack" for attack roll, "save" for saving throw
        """
        # Auto-calculate damage if not provided
        if damage_dice is None:
            # Base on creature size and strength
            creature_size = getattr(creature, 'size', 'Medium')
            str_score = creature.stats.get('str', 10)
            
            if creature_size == 'Tiny':
                damage_dice = "1d4"
            elif creature_size == 'Small':
                damage_dice = "1d6" 
            elif creature_size == 'Medium':
                damage_dice = "1d6"
            elif creature_size == 'Large':
                damage_dice = "2d6"
            elif creature_size == 'Huge':
                damage_dice = "2d8"
            elif creature_size == 'Gargantuan':
                damage_dice = "3d8"
            else:
                damage_dice = "1d6"  # Default
        
        # Auto-generate attack name if not provided
        if attack_name is None:
            attack_name = f"{creature.name} Grapple"
        
        return UniversalGrappleActions.create_grapple_attack_action(
            damage_dice=damage_dice,
            attack_name=attack_name,
            damage_type=damage_type,
            range_ft=range_ft,
            method=method
        )
    
    @staticmethod
    def attempt_grapple(attacker, target, **kwargs):
        """Standardized grapple attempt for any creature."""
        return UniversalGrappling.attempt_grapple(attacker, target, **kwargs)
    
    @staticmethod
    def attempt_escape(grappled_creature, action_type="ACTION"):
        """Standardized escape attempt for any creature."""
        return UniversalGrappling.attempt_escape(grappled_creature, action_type)
    
    @staticmethod
    def apply_grapple_conditions(grappler, target, escape_dc, additional_conditions=None):
        """
        Apply grapple conditions with optional additional effects.
        
        Args:
            grappler: Creature doing the grappling
            target: Creature being grappled
            escape_dc: DC to escape
            additional_conditions: List of additional conditions to apply
        """
        # Apply standard grapple conditions
        GrappleConditionManager.apply_grappled_condition(target, grappler, escape_dc)
        GrappleConditionManager.apply_grappling_condition(grappler, target)
        
        # Apply additional conditions (like Restrained for octopus)
        if additional_conditions:
            for condition in additional_conditions:
                if condition == 'Restrained':
                    target.is_restrained = True
                    print(f"** {target.name} also has the Restrained condition! **")
                elif condition == 'Prone':
                    target.is_prone = True
                    print(f"** {target.name} also has the Prone condition! **")
                # Add more conditions as needed
    
    @staticmethod
    def end_grapple(grappler, target):
        """Standardized grapple ending for any creatures."""
        # Remove additional conditions first
        if hasattr(target, 'is_restrained'):
            target.is_restrained = False
            print(f"** {target.name} is no longer restrained **")
        
        # Then remove standard grapple conditions
        GrappleConditionManager.end_grapple(grappler, target)
    
    @staticmethod
    def validate_all_grapples(combatants):
        """Validate all grapple states for all combatants."""
        for combatant in combatants:
            GrappleConditionManager.validate_grapple_state(combatant)
    
    @staticmethod
    def get_grapple_attack_bonus(creature):
        """Calculate standard grapple attack bonus for a creature."""
        str_mod = get_ability_modifier(creature.stats.get('str', 10))
        prof_bonus = creature.get_proficiency_bonus()
        return str_mod + prof_bonus
    
    @staticmethod
    def get_grapple_escape_dc(grappler):
        """Calculate standard escape DC for a grappler."""
        str_mod = get_ability_modifier(grappler.stats.get('str', 10))
        prof_bonus = grappler.get_proficiency_bonus()
        return 8 + str_mod + prof_bonus
    
    @staticmethod
    def create_standard_escape_action():
        """Create a standard escape action any creature can use."""
        return UniversalGrappleActions.create_escape_action()


class CreatureGrappleProfile:
    """
    Template for creature-specific grappling behavior.
    Defines how a particular type of creature should grapple.
    """
    
    def __init__(self, creature_name, grapple_method="attack", additional_conditions=None,
                 damage_dice=None, range_ft=5, special_rules=None):
        self.creature_name = creature_name
        self.grapple_method = grapple_method  # "attack" or "save"
        self.additional_conditions = additional_conditions or []
        self.damage_dice = damage_dice
        self.range_ft = range_ft
        self.special_rules = special_rules or {}
    
    def apply_to_creature(self, creature):
        """Apply this grapple profile to a creature."""
        # Create the appropriate grapple action
        grapple_action = GlobalGrappleManager.create_creature_grapple_attack(
            creature=creature,
            damage_dice=self.damage_dice,
            range_ft=self.range_ft,
            method=self.grapple_method
        )
        
        # Add escape action
        escape_action = GlobalGrappleManager.create_standard_escape_action()
        
        # Add to creature's available actions
        creature.available_actions.append(grapple_action)
        creature.available_actions.append(escape_action)
        
        # Store profile for reference
        creature.grapple_profile = self


# Pre-defined grapple profiles for common creature types
GRAPPLE_PROFILES = {
    'humanoid_unarmed': CreatureGrappleProfile(
        creature_name="Humanoid (Unarmed)",
        grapple_method="attack",
        damage_dice="1d4",
        range_ft=5
    ),
    
    'giant_constrictor_snake': CreatureGrappleProfile(
        creature_name="Giant Constrictor Snake",
        grapple_method="save",
        damage_dice="2d8",
        range_ft=10,
        special_rules={'crush_action': True}
    ),
    
    'giant_octopus': CreatureGrappleProfile(
        creature_name="Giant Octopus",
        grapple_method="attack",
        additional_conditions=['Restrained'],  # PHB 2024: all tentacles = restrained
        damage_dice="2d6",
        range_ft=10,
        special_rules={'single_target_all_limbs': True}
    ),
    
    'roper': CreatureGrappleProfile(
        creature_name="Roper",
        grapple_method="save",
        damage_dice="1d6",
        range_ft=50,
        special_rules={'multiple_tendrils': True, 'max_grapples': 4}
    )
}


def setup_creature_grappling(creature, profile_name=None):
    """
    Setup grappling for a creature using a pre-defined profile or auto-detection.
    
    Args:
        creature: The creature to setup
        profile_name: Name of profile to use, or None for auto-detection
    """
    if profile_name and profile_name in GRAPPLE_PROFILES:
        profile = GRAPPLE_PROFILES[profile_name]
        profile.apply_to_creature(creature)
        print(f"Applied grapple profile '{profile_name}' to {creature.name}")
    else:
        # Auto-detect based on creature type/name
        if 'Octopus' in creature.name:
            setup_creature_grappling(creature, 'giant_octopus')
        elif 'Snake' in creature.name and 'Constrictor' in creature.name:
            setup_creature_grappling(creature, 'giant_constrictor_snake')
        elif hasattr(creature, 'creature_type') and creature.creature_type == 'Humanoid':
            setup_creature_grappling(creature, 'humanoid_unarmed')
        else:
            # Default profile
            profile = CreatureGrappleProfile(
                creature_name=f"Generic {creature.name}",
                grapple_method="attack"
            )
            profile.apply_to_creature(creature)
            print(f"Applied default grapple profile to {creature.name}")
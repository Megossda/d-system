# File: systems/grappling/grapple_conditions.py
"""
Grapple condition management - PHB 2024 compliant.
Handles the Grappled and Grappling conditions universally.
"""


class GrappleConditionManager:
    """Manages grapple-related conditions for all creatures."""

    @staticmethod
    def apply_grappled_condition(target, grappler, escape_dc):
        """
        Apply the Grappled condition to a target.
        PHB 2024: Speed 0, disadvantage on attacks vs others.
        """
        target.is_grappled = True
        target.grappler = grappler
        target.grapple_escape_dc = escape_dc
        
        # Store original speed for restoration
        if not hasattr(target, '_original_speed'):
            target._original_speed = target.speed
        target.speed = 0
        
        print(f"** {target.name} gains the Grappled condition **")
        return True

    @staticmethod
    def apply_grappling_condition(grappler, target):
        """
        Apply the Grappling condition to a grappler.
        PHB 2024: Can only grapple one creature per 'hand/body part'.
        """
        grappler.is_grappling = True
        grappler.grapple_target = target
        
        print(f"** {grappler.name} is now grappling {target.name} **")
        return True

    @staticmethod
    def remove_grappled_condition(target):
        """Remove the Grappled condition and restore normal state."""
        if hasattr(target, 'is_grappled'):
            target.is_grappled = False
        
        # Restore original speed
        if hasattr(target, '_original_speed'):
            target.speed = target._original_speed
            delattr(target, '_original_speed')
        
        # Clean up grapple references
        if hasattr(target, 'grappler'):
            delattr(target, 'grappler')
        if hasattr(target, 'grapple_escape_dc'):
            delattr(target, 'grapple_escape_dc')
        
        print(f"** {target.name} is no longer grappled **")

    @staticmethod
    def remove_grappling_condition(grappler):
        """Remove the Grappling condition from a grappler."""
        if hasattr(grappler, 'is_grappling'):
            grappler.is_grappling = False
        if hasattr(grappler, 'grapple_target'):
            grappler.grapple_target = None
        
        print(f"** {grappler.name} is no longer grappling **")

    @staticmethod
    def has_grappled_condition(creature):
        """Check if a creature has the Grappled condition."""
        return hasattr(creature, 'is_grappled') and creature.is_grappled

    @staticmethod
    def has_grappling_condition(creature):
        """Check if a creature has the Grappling condition."""
        return hasattr(creature, 'is_grappling') and creature.is_grappling

    @staticmethod
    def get_grapple_disadvantage_targets(grappled_creature, potential_targets):
        """
        Get list of targets that the grappled creature has disadvantage against.
        PHB 2024: Disadvantage on attacks against any target other than the grappler.
        """
        if not GrappleConditionManager.has_grappled_condition(grappled_creature):
            return []
        
        grappler = getattr(grappled_creature, 'grappler', None)
        if not grappler:
            return []
        
        # Disadvantage against everyone except the grappler
        disadvantage_targets = [target for target in potential_targets if target != grappler]
        return disadvantage_targets

    @staticmethod
    def validate_grapple_state(creature):
        """
        Validate and clean up invalid grapple states.
        Should be called during turn processing.
        """
        # Clean up grappling state
        if GrappleConditionManager.has_grappling_condition(creature):
            target = getattr(creature, 'grapple_target', None)
            if not target or not target.is_alive or not GrappleConditionManager.has_grappled_condition(target):
                print(f"** Invalid grappling state detected for {creature.name}, cleaning up **")
                GrappleConditionManager.remove_grappling_condition(creature)

        # Clean up grappled state
        if GrappleConditionManager.has_grappled_condition(creature):
            grappler = getattr(creature, 'grappler', None)
            if not grappler or not grappler.is_alive or not GrappleConditionManager.has_grappling_condition(grappler):
                print(f"** Invalid grappled state detected for {creature.name}, cleaning up **")
                GrappleConditionManager.remove_grappled_condition(creature)

    @staticmethod
    def end_grapple(grappler, target):
        """
        Properly end a grapple between two creatures.
        Cleans up both sides of the relationship.
        """
        GrappleConditionManager.remove_grappling_condition(grappler)
        GrappleConditionManager.remove_grappled_condition(target)
        print(f"** Grapple between {grappler.name} and {target.name} has ended **")
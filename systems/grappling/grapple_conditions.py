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
        
        # CRITICAL FIX: Also remove creature-specific conditions like Restrained
        if hasattr(target, 'is_restrained'):
            target.is_restrained = False
            print(f"** {target.name} is no longer restrained **")
        
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
    def is_incapacitated(creature):
        """
        CRITICAL FIX: Check if a creature is incapacitated.
        PHB 2024: Incapacitated condition or any condition that includes it.
        """
        # Debug: Let's see what conditions the creature actually has
        debug_conditions = []
        
        # Direct incapacitation
        if hasattr(creature, 'is_incapacitated') and creature.is_incapacitated:
            debug_conditions.append('is_incapacitated')
            return True
        
        # Conditions that include incapacitation (PHB 2024)
        incapacitating_conditions = [
            'is_paralyzed',    # Paralyzed includes Incapacitated
            'is_stunned',      # Stunned includes Incapacitated  
            'is_unconscious',  # Unconscious includes Incapacitated
            'is_petrified'     # Petrified includes Incapacitated
        ]
        
        for condition in incapacitating_conditions:
            if hasattr(creature, condition) and getattr(creature, condition):
                debug_conditions.append(condition)
                return True
        
        # If we get here, no incapacitation was detected
        # This should help us debug why it's not working
        if debug_conditions:
            print(f"DEBUG: {creature.name} has conditions: {debug_conditions}")
        
        return False

    @staticmethod
    def validate_grapple_state(creature):
        """FIXED: Now properly handles incapacitation."""
        # CRITICAL FIX: Check for incapacitation first
        is_incap = GrappleConditionManager.is_incapacitated(creature)
        
        if is_incap:
            print(f"DEBUG: {creature.name} is incapacitated, ending all grapples...")
            if GrappleConditionManager.has_grappling_condition(creature):
                target = getattr(creature, 'grapple_target', None)
                print(f"DEBUG: {creature.name} has grappling condition, target: {target.name if target else None}")
                
                if target:
                    print(f"** {creature.name} becomes incapacitated - all grapples end immediately! **")
                    print(f"DEBUG: About to call end_grapple with target")
                    GrappleConditionManager.end_grapple(creature, target)
                    print(f"DEBUG: end_grapple completed")
                else:
                    print(f"** {creature.name} becomes incapacitated - cleaning up invalid grapple state! **")
                    
                    import gc
                    for obj in gc.get_objects():
                        if (hasattr(obj, 'is_grappled') and getattr(obj, 'is_grappled', False) and 
                            hasattr(obj, 'grappler') and getattr(obj, 'grappler', None) == creature):
                            print(f"** Found grappled target {obj.name}, releasing... **")
                            print(f"DEBUG: About to call end_grapple with found target")
                            GrappleConditionManager.end_grapple(creature, obj)
                            print(f"DEBUG: end_grapple completed with found target")
                            return
                    
                    print(f"** No grappled target found, cleaning up grappler state only **")
                    GrappleConditionManager.remove_grappling_condition(creature)
            return

        # Clean up grappling state
        if GrappleConditionManager.has_grappling_condition(creature):
            target = getattr(creature, 'grapple_target', None)
            if not target or not target.is_alive or not GrappleConditionManager.has_grappled_condition(target):
                print(f"** Invalid grappling state detected for {creature.name}, cleaning up **")
                if target:
                    GrappleConditionManager.end_grapple(creature, target)
                else:
                    GrappleConditionManager.remove_grappling_condition(creature)

        # Clean up grappled state  
        if GrappleConditionManager.has_grappled_condition(creature):
            grappler = getattr(creature, 'grappler', None)
            if not grappler or not grappler.is_alive or not GrappleConditionManager.has_grappling_condition(grappler):
                print(f"** Invalid grappled state detected for {creature.name}, cleaning up **")
                if grappler:
                    GrappleConditionManager.end_grapple(grappler, creature)
                else:
                    GrappleConditionManager.remove_grappled_condition(creature)

    @staticmethod
    def end_grapple(grappler, target):
        """
        CRITICAL FIX: Properly end a grapple between two creatures.
        Cleans up both sides of the relationship.
        """
        print(f"DEBUG: end_grapple called - grappler: {grappler.name}, target: {target.name}")
        
        # CRITICAL FIX: Call the creature's own release_grapple method if it exists
        if hasattr(grappler, 'release_grapple'):
            print(f"DEBUG: Using {grappler.name}'s release_grapple method")
            grappler.release_grapple(target)
        else:
            print(f"DEBUG: Using manual cleanup for {grappler.name}")
            # Fallback to manual cleanup
            # Remove creature-specific conditions first (like Restrained for Giant Octopus)
            if hasattr(target, 'is_restrained'):
                print(f"DEBUG: Removing restrained condition from {target.name}")
                target.is_restrained = False
                print(f"** {target.name} is no longer restrained **")
            
            # Remove standard grapple conditions from TARGET
            print(f"DEBUG: Removing grappled condition from {target.name}")
            GrappleConditionManager.remove_grappled_condition(target)
            
            # Remove grappling condition from GRAPPLER  
            print(f"DEBUG: Removing grappling condition from {grappler.name}")
            GrappleConditionManager.remove_grappling_condition(grappler)
            
            print(f"** Grapple between {grappler.name} and {target.name} has ended **")
        
        print(f"DEBUG: end_grapple finished - grappler.is_grappling: {getattr(grappler, 'is_grappling', 'NONE')}, target.is_grappled: {getattr(target, 'is_grappled', 'NONE')}")
# File: systems/conditions/__init__.py
"""Global condition system."""

def validate_creature_conditions(creature):
    """Validate all conditions on a creature."""
    # Check for condition interactions and cleanup invalid states
    
    # Unconscious includes Incapacitated
    if getattr(creature, 'is_unconscious', False):
        creature.is_incapacitated = True
    
    # Paralyzed includes Incapacitated  
    if getattr(creature, 'is_paralyzed', False):
        creature.is_incapacitated = True
    
    # Speed 0 for certain conditions
    if getattr(creature, 'is_grappled', False) or getattr(creature, 'is_restrained', False):
        if hasattr(creature, '_original_speed'):
            creature.speed = 0
    
    # Clean up dead creature conditions
    if not creature.is_alive:
        cleanup_dead_creature_conditions(creature)

def cleanup_dead_creature_conditions(creature):
    """Clean up conditions when creature dies."""
    # Remove conditions that don't persist after death
    temporary_conditions = [
        'is_grappled', 'is_grappling', 'is_restrained', 'is_charmed',
        'is_frightened', 'is_stunned', 'is_paralyzed'
    ]
    
    for condition in temporary_conditions:
        if hasattr(creature, condition):
            setattr(creature, condition, False)
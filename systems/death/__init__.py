# File: systems/death/__init__.py
"""Global death handling system."""

def handle_creature_death(creature):
    """Handle creature death using global systems."""
    print(f"** {creature.name} dies! **")
    
    # Release any grapples
    if getattr(creature, 'is_grappling', False):
        from systems.grappling.grapple_manager import GlobalGrappleManager
        if hasattr(creature, 'grapple_target') and creature.grapple_target:
            GlobalGrappleManager.end_grapple(creature, creature.grapple_target)
    
    # Clean up conditions
    from systems.conditions import cleanup_dead_creature_conditions
    cleanup_dead_creature_conditions(creature)
    
    # Break concentration
    if hasattr(creature, 'concentrating_on'):
        creature.concentrating_on = None
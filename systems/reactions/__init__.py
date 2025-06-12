# File: systems/reactions/__init__.py
"""Global reaction system."""

def can_use_reaction(creature, reaction_name):
    """Check if creature can use a reaction."""
    # Check if reaction is available this turn
    if getattr(creature, 'has_used_reaction', False):
        return False
    
    # Check trait-specific availability
    from systems.creature_traits import get_trait
    trait = get_trait(creature, reaction_name)
    if trait and trait.get('used_today', False):
        return False
    
    return True

def use_reaction(creature, reaction_name):
    """Mark reaction as used."""
    creature.has_used_reaction = True
    print(f"** {creature.name} uses {reaction_name} reaction **")
# File: systems/creature_traits/__init__.py
"""Global creature traits system."""

def add_trait(creature, trait_data):
    """Add a trait to a creature."""
    if not hasattr(creature, 'traits'):
        creature.traits = []
    creature.traits.append(trait_data)

def get_trait(creature, trait_name):
    """Get a specific trait by name."""
    if not hasattr(creature, 'traits'):
        return None
    
    for trait in creature.traits:
        if trait.get('name') == trait_name:
            return trait
    return None

def use_trait(creature, trait_name):
    """Mark a trait as used."""
    trait = get_trait(creature, trait_name)
    if trait and 'used_today' in trait:
        trait['used_today'] = True
        print(f"** {creature.name} uses {trait_name} trait **")
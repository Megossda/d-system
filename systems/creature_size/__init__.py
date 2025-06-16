# File: systems/creature_size/__init__.py
"""
Global system for managing creature size categories and rules.
This centralizes all size-related logic for d-system.
"""

# PHB 2024 Size Categories
TINY = "Tiny"
SMALL = "Small"
MEDIUM = "Medium"
LARGE = "Large"
HUGE = "Huge"
GARGANTUAN = "Gargantuan"

# A list of all size categories in order for easy comparison
SIZE_ORDER = [TINY, SMALL, MEDIUM, LARGE, HUGE, GARGANTUAN]

# A dictionary mapping common species/races to their default size
# This can be expanded as more species are added to the game.
SPECIES_TO_SIZE = {
    "Human": MEDIUM,
    "Elf": MEDIUM,
    "Dwarf": MEDIUM,
    "Halfling": SMALL,
    "Gnome": SMALL,
    "Dragonborn": MEDIUM,
    "Tiefling": MEDIUM,
    "Orc": MEDIUM,
    # Default for enemies or unspecified creatures
    "Goblin": SMALL,
    "Hobgoblin": MEDIUM,
    "Giant Octopus": LARGE,
    "Default": MEDIUM
}

def get_size_for_species(species_name):
    """
    Gets the default size for a given species name.
    Falls back to Medium if the species is not found.
    """
    return SPECIES_TO_SIZE.get(species_name, MEDIUM)

def can_grapple_size(grappler_size, target_size, max_difference=1):
    """
    Checks if a creature of a certain size can grapple a target of another size.
    Based on PHB 2024 rules: Target can be no more than one size larger.
    """
    try:
        grappler_idx = SIZE_ORDER.index(grappler_size)
        target_idx = SIZE_ORDER.index(target_size)
        
        # Target's index must be less than or equal to the grappler's index + max_difference
        return target_idx <= (grappler_idx + max_difference)
    except (ValueError, IndexError):
        # If size is not found in the standard list, default to a safe check
        print(f"Warning: Unknown size category used ('{grappler_size}' or '{target_size}'). Defaulting grapple check to False.")
        return False

def get_size_modifier(size):
    """
    Returns any modifiers associated with a size category.
    (Placeholder for future mechanics like carrying capacity modifiers).
    """
    # Currently, there are no direct combat modifiers for size in PHB 2024,
    # but this function is here for future expansion.
    return 0


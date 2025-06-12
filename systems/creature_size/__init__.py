# File: systems/creature_size/__init__.py
"""Global creature size system."""

def can_grapple_size(grappler_size, target_size, max_difference=1):
    """Check if grappler can grapple target based on size."""
    size_order = ['Tiny', 'Small', 'Medium', 'Large', 'Huge', 'Gargantuan']
    
    try:
        grappler_idx = size_order.index(grappler_size)
        target_idx = size_order.index(target_size)
        return target_idx <= grappler_idx + max_difference
    except ValueError:
        return True  # Unknown sizes default to allowed
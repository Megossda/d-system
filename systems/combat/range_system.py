# File: systems/combat/range_system.py
"""Global range system."""

def check_weapon_range(attacker, target, weapon):
    """Check if target is within weapon range."""
    distance = abs(attacker.position - target.position)
    weapon_range = getattr(weapon, 'reach', 5)
    return distance <= weapon_range
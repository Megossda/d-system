# File: systems/movement/__init__.py
"""Global movement system."""

def move_creature(creature, distance, direction):
    """Move a creature using global movement rules."""
    if direction == 'away_from_threat':
        # Simple implementation: move backward
        creature.position += distance
    elif direction == 'toward_target':
        creature.position -= distance
    
    print(f"** {creature.name} moves {distance}ft to position {creature.position} **")
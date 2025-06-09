"""Magic system - spells organized by level and school."""

# Import commonly used spells
from .level_1.cure_wounds import cure_wounds
from .level_1.guiding_bolt import guiding_bolt
from .level_1.searing_smite import searing_smite

__all__ = ['cure_wounds', 'guiding_bolt', 'searing_smite']
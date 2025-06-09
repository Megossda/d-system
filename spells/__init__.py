# File: spells/__init__.py
"""Magic system - spells organized by level and school."""

# Import commonly used spells
from .level_1.cure_wounds import cure_wounds
from .level_1.guiding_bolt import guiding_bolt
from .level_1.searing_smite import searing_smite

__all__ = ['cure_wounds', 'guiding_bolt', 'searing_smite']

# File: spells/level_1/__init__.py
"""1st level spells."""

from .cure_wounds import cure_wounds
from .guiding_bolt import guiding_bolt
from .searing_smite import searing_smite
from .heroism import heroism
from .bless import bless

__all__ = ['cure_wounds', 'guiding_bolt', 'searing_smite', 'heroism', 'bless']
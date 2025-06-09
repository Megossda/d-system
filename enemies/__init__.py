# File: enemies/__init__.py
"""Enemy creatures organized by challenge rating."""

from .cr_0_quarter.goblin import Goblin
from .cr_half_1.hobgoblin_warrior import HobgoblinWarrior
from .cr_2_5.giant_constrictor_snake import GiantConstrictorSnake

__all__ = ['Goblin', 'HobgoblinWarrior', 'GiantConstrictorSnake']










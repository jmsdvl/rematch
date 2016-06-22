__version__ = '1.0.dev0'

from .parser import (LiteralExpr, NullString, StarExpr, ChoiceExpr, ConcatExpr,
                     TreeNode, parse, walk_tree, level_first_walk)
from .patcher import State, Arrow, DotArrow, Epsilon, patch
from .regex import Regex, transition, E_set, partition

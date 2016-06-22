"""
parsing.py: part of `rematch`, a pure-Python implementation of an NFA based
regular expression matching engine.

This module exposes the tools & classes necessary to turn the string
representation of a regular language into an expression tree of semantically
valued nodes.
"""

from collections import deque, namedtuple
from functools import reduce
from itertools import takewhile
from string import ascii_letters, digits

TreeNode = namedtuple('TreeNode', 'left right')
TreeNode.__doc__ = """ Base class for building Tree like structures.

These particular tree like structures are anonymous: values are only stored in
leaves.  Each leaf is represented as a TreeNode with a value in the left branch
in place of another TreeNode and the right branch set to None.

Attributes (writable):
    left, right (TreeNode(s)): the children of the node

Note: as a namedtuple, the left and right branches can also be accessed via
indexing at positions 0 and 1, respectively.
"""


class LiteralExpr(TreeNode):
    """ Any single literal character, epsilon, and '.'
    """
    __slots__ = ()

    def __new__(cls, value):
        return super(LiteralExpr, cls).__new__(cls, left=value, right=None)

    @property
    def value(self):
        return self.left


class NullString(TreeNode):
    """ The null string, '' """
    __slots__ = ()

    def __new__(cls):
        return super(NullString, cls).__new__(cls, left=None, right=None)


class StarExpr(TreeNode):
    """ The star operator (star, '*').
    """
    __slots__ = ()

    def __new__(cls, operand):
        return super(StarExpr, cls).__new__(cls, left=operand, right=None)

    @property
    def repetand(self):
        return self.left


class ChoiceExpr(TreeNode):
    """ The alternation operator (pipe, '|').
    """
    __slots__ = ()

    def __new__(cls, left, right):
        return super(ChoiceExpr, cls).__new__(cls, left=left, right=right)


class ConcatExpr(TreeNode):
    """ ConcatExprenation: the basic operator.
    """
    __slots__ = ()

    def __new__(cls, left, right):
        return super(ConcatExpr, cls).__new__(cls, left=left, right=right)


class DotExpr(TreeNode):
    __slots__ = ()

    def __new__(cls):
        return super(DotExpr, cls).__new__(cls, left='.', right=None)


class CharClassExpr(TreeNode):
    __slots__ = ()

    def __new__(cls, values):
        return super(CharClassExpr, cls).__new__(cls, left=values, right=None)

    @property
    def charset(self):
        return self.left


def parse(regex):
    """ Turn a string regex into an expression tree.

    This function will transform the string representation of a regular
    expression into an expression tree using the LiteralExpr, StarExpr,
    ChoiceExpr, and ConcatExpr classes.  NullString, a special form of a
    LiteralExpr, is also used.  `parse` handles parentheses and alternation by
    recursing into the component subexpressions; the rest are handled via a
    simple stack structure.

    Supported Syntax:
        literals (including the '.' metacharacter)
        The Kleene star (asterisk, '*')
        Alternation (pipe, '|')
        The One or More quantifier (plus, '+')
        The Zero or One quantifier (question mark, '?')
        The backslash for escaping special characters ('\\')
        Parentheses for grouping.
    """
    # TODO: character class metachars need special handling too
    if not regex:
        return NullString()
    RE = iter(regex)
    stack = deque()
    for ch in RE:
        if ch == '(':
            stack.append(parse(RE))
        elif ch == ')':
            return reduce(ConcatExpr, stack)
        elif ch == '.':
            stack.append(DotExpr())

        elif ch == '[':
            values = list(takewhile(lambda x: x != ']', RE))
            print(values)
            stack.append(CharClassExpr(values=values))

        elif ch == '*':
            op = stack.pop()
            stack.append(StarExpr(op))
        elif ch == '?':
            op = stack.pop()
            stack.append(ChoiceExpr(op, NullString()))
        elif ch == '+':
            op = stack.pop()
            stack.append(ConcatExpr(op, StarExpr(op)))
        elif ch == '|':
            left = reduce(ConcatExpr, stack)
            stack.clear()
            right = parse(RE)
            stack.append(ChoiceExpr(left, right))
        elif ch == '\\':
            ch = next(RE)
            stack.append(LiteralExpr(ch))
        else:
            stack.append(LiteralExpr(ch))
    stack = reduce(ConcatExpr, stack)
    return stack


def walk_tree(tree):
    """ walks the tree 'in-order' style (not pre or post order). """
    if tree is None:
        yield
    if isinstance(tree, LiteralExpr):
        yield tree.value, tree.__class__.__name__
    else:
        if tree.left:
            yield from walk_tree(tree.left)
        yield tree.__class__.__name__
        if tree.right:
            yield from walk_tree(tree.right)


def level_first_walk(tree):
    """ Walks a tree in level first order (basically BFS) """
    queue = deque()
    queue.append(tree)
    while queue:
        current = queue.popleft()
        yield current.__class__.__name__
        if isinstance(current, LiteralExpr):
            yield current.value
            continue
        if current.left:
            queue.append(current.left)
        if current.right:
            queue.append(current.right)

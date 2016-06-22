"""
patcher.py: tools to convert an expression tree returned by `parser.parse` into
an NFA machine-state graph.
"""

from itertools import count
from functools import singledispatch

from .parser import (LiteralExpr, StarExpr, ChoiceExpr, ConcatExpr,
                     CharClassExpr, DotExpr, NullString, parse)


class State(list):
    """ A State is one of the three basic building blocks of an NFA.
    Essentially the State object is just a container for outgoing arrows.
    """
    Index = count()

    @property
    def arrows(self):
        return self

    def __init__(self, *arrows):
        super(State, self).__init__(arrows)
        self.id = next(State.Index)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        arrows = list(self.arrows)
        return 'State {} holding {}'.format(self.id, arrows)

    def __eq__(self, other):
        return self.id == other.id

    def __add__(self, other):
        new_state = State()
        new_state.extend(self)
        new_state.extend(other)
        return new_state

    def __hash__(self):
        return hash(self.id)


class Arrow(object):
    """ The Arrow is one of the basic building blocks of an NFA.  The Arrow
    object represents a directed labelled edge on an NFA graph.  In this
    implementation, the arrow is a callable object: calling the arrow will
    return either the state it points at, if it is called with the right
    value(s), or None.
    """
    def __init__(self, value, pointsAt=None):
        self.pointsAt = pointsAt
        self.value = value

    def __call__(self, value):
        # FIXME: this version of handling a character class doesn't actually
        # work, there's no way to match a literal period, for example.
        if self.value == value:
            return self.pointsAt
        return None

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'Arrow: {} to {}'.format(self.value, self.pointsAt)


class DotArrow(Arrow):
    def __init__(self, pointsAt=None):
        self.pointsAt = pointsAt

    def __call__(self, inp):
        if inp:
            return self.pointsAt
        return None


class Epsilon(Arrow):
    """ An Epsilon Arrow is one of the basic building blocks of an NFA.
    Basically an epsilon arrow 'clones' the operation of the machine - at every
    state transition, all epsilon arrows are followed automatically and the
    resulting state set added to the current states of the machine.
    """
    def __init__(self, pointsAt=None):
        self.pointsAt = pointsAt
        self.value = None

    def __call__(self, value=None):
        return self.pointsAt

    def __str__(self):
        return 'Epsilon arrow pointing at {}'.format(self.pointsAt.id)


class CharClassArrow(Arrow):
    def __init__(self, values, pointsAt=None):
        self.values = values
        self.pointsAt = pointsAt

    def __call__(self, inp):
        if inp in self.values:
            return self.pointsAt
        return None


@singledispatch
def patch(obj):
    """ Construct an NFA from an expression tree.

    `patch` calls itself recursively to convert an expression tree into a
    suitable NFA represented as a graph with three kinds of obects: States,
    which are collections of outgoing arrows, (labeled) Arrows, and Epsilon
    arrows.

    Arguments:
        Tree (tree): a formatted tree of objects (returned by `parser.parse`)

    Returns:
        start, accept (tuple): the first element of the return tuple is the
        NFA's starting State object, the second is a `list` of State objects
        representing the NFA's set of accept states
    """
    raise TypeError("No patch handler found for object {}".format(obj))


@patch.register(CharClassExpr)
def charclass_patch(obj):
    accept = State()
    conn = CharClassArrow(values=obj.charset, pointsAt=accept)
    start = State(conn)
    return (start, [accept])


@patch.register(DotExpr)
def dot_patch(obj):
    accept = State()
    conn = DotArrow(pointsAt=accept)
    start = State(conn)
    return (start, [accept])


@patch.register(NullString)
def null_patch(obj):
    exit = start = State()
    return (start, [exit])


@patch.register(LiteralExpr)
def literal_patch(obj):
    accept = State()
    conn = Arrow(obj.value, pointsAt=accept)
    start = State(conn)
    return (start, [accept])


@patch.register(ConcatExpr)
def concat_patch(obj):
    L_start, L_accept = patch(obj.left)
    R_start, R_accept = patch(obj.right)
    bridge = Epsilon(pointsAt=R_start)
    for state in L_accept:
        state.append(bridge)
    return (L_start, R_accept)


@patch.register(ChoiceExpr)
def choice_patch(obj):
    L_start, L_accept = patch(obj.left)
    R_start, R_accept = patch(obj.right)
    L_bridge, R_bridge = Epsilon(pointsAt=L_start), Epsilon(pointsAt=R_start)
    Split = State(L_bridge, R_bridge)
    return (Split, L_accept + R_accept)


@patch.register(StarExpr)
def star_patch(obj):
    Rep_start, Rep_accept = patch(obj.repetand)
    eps_in = Epsilon(pointsAt=Rep_start)
    dummy_entrance = State(eps_in)
    for state in Rep_accept:
        eps = Epsilon(pointsAt=Rep_start)
        state.append(eps)
    return (dummy_entrance, Rep_accept + [dummy_entrance])

"""
regex.py: tools to run an NFA state machine graph against a string.
"""

from itertools import tee, filterfalse
from functools import reduce

from .patcher import Epsilon, patch
from .parser import parse


class Regex(object):
    """ Evaluate the argument against the internally 'compiled' RegEx.

    After construction, the Regex object stores the generated NFA
    internally.  Each time the Regex matching object is run, it keeps a
    'finger' on each state that the NFA is in.  At the end of the
    computation, if any 'finger' is on the Match state, the computation
    returns True.
    """
    def __init__(self, pattern):
        self.pattern = pattern
        start, accept = patch(parse(pattern))
        self.start = set(E_set(start))  # remove set if not using yeild impl.
        self.accept = set(accept)

    def __call__(self, string):
        curr = self.start
        for char in string:
            next_states = [transition(st, char) for st in curr]
            if not next_states:
                break
            curr = reduce(set.union, next_states)
        return not curr.isdisjoint(self.accept)


def transition(state, inp):
    """ The transition function for a state given an input for an NFA.

    Arguments:
        state (State): the state from which to calculate
        inp (char): the character being matched

    Returns:
        Set: the next set of active states determined by the input state and
             char.
    """
    valued_arrows, _ = partition(lambda x: isinstance(x, Epsilon), state)
    proximates = set([arr(inp) for arr in valued_arrows])
    proximates.discard(None)

    extended = set()
    for state in proximates:
        extended.update(set(E_set(state)))

    return proximates.union(extended)


def E_set(state, followed=None):
    """ The set E(x), all states reachable from state `x` by following e arrows.

    Arguments:
        state (State): the location in the NFA to start searching from
        followed (None): this keyword argument is used internally to avoid
                         potential infinite recursion; don't use it explicitly.

    Yields:
        A Generator-Iterator over a stream of State objects.
    """
    #  Needs to be passed into some kind of constructor that will consume all
    #  the subgenerators
    epsilons = [arr for arr in state if isinstance(arr, Epsilon)]
    if not followed:
        followed = set(epsilons)
    else:
        epsilons = [arr for arr in epsilons if arr not in followed]
        followed |= set(epsilons)
    for arrow in epsilons:
        yield from E_set(arrow(), followed)
    yield state


def partition(pred, iterable):
    """ Splits the iterable along the predicate.

    Arguments:
        pred (callable): should return True or False when applied to an element
                         of the iterable
        iterable: any object supporting the iterable protocol

    Returns:
        A 2-tuple. The first element is the items of `iterable` that tested
        false, the second those that tested true.
    """
    t1, t2 = tee(iterable)
    return filterfalse(pred, t1), filter(pred, t2)

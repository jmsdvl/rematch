import string

import pytest

from rematch import (State, Arrow, Epsilon, DotArrow, patch, parse, TreeNode,
                     Regex, transition, E_set, partition)

CHARS = string.ascii_letters + string.digits

# TODO:
#   Re-evaluate tests and make sure we're covering what needs to be covered

def test_patch_raises_for_unknown_object():
    with pytest.raises(TypeError):
        patch(object)


def test_state():
    A = State()
    assert type(A) is State
    assert A.id == 0


def test_state_concat():
    A = State('green', 'blue')
    B = State('this', 'that')
    C = A + B
    assert type(C) is State
    for item, string in zip(C, 'green blue this that'.split()):
        item == string


def test_states_are_hashable():
    A = State('green', 'blue')
    B = State('this', 'that')
    state_set = {A, B}
    for item in state_set:
        assert type(item) is State


def test_Arrow_only_returns_for_correct_value():
    some_state = State()
    some_arr = Arrow('v', some_state)
    assert some_arr('v') is some_state
    for char in CHARS.replace('v', ''):
        assert some_arr(char) is not some_state


def test_anychar_arrow_returns_for_all_values():
    some_state = State()
    any_arr = DotArrow(some_state)
    for char in CHARS:
        assert any_arr(char) is some_state


def test_epsilon_arrow_returns_for_all_values():
    some_state = State()
    eps = Epsilon(some_state)
    for char in CHARS:
        assert eps(char) is some_state


def test_E_set():
    epA, epB = Epsilon(), Epsilon()
    A, B, C = State(epA), State(epB), State()
    epA.pointsAt = B
    epB.pointsAt = C
    followed = set(E_set(A))
    assert A in followed
    assert B in followed
    assert C in followed
    assert set([A, B, C]) == followed


def test_transitions_no_epsilon():
    arrA, arrB = Arrow('a'), Arrow('b')
    A, B, C = State(arrA), State(arrB), State()
    arrA.pointsAt = B
    arrB.pointsAt = C
    from_A_with_a = transition(A, 'a')
    assert {B} == from_A_with_a
    from_A_with_b = transition(A, 'b')
    assert set() == from_A_with_b
    from_B_with_a = transition(B, 'a')
    assert set() == from_B_with_a
    from_B_with_b = transition(B, 'b')
    assert {C} == from_B_with_b


def test_chaining_transitions():
    arrA, arrB = Arrow('a'), Arrow('b')
    A, B, C = State(arrA), State(arrB), State()
    arrA.pointsAt = B
    arrB.pointsAt = C
    assert {C} == transition(*transition(A, 'a'), 'b')


def test_epsilon_cycle_doesnt_recurse_forever():
    A, B = State(), State()
    e1, e2 = Epsilon(), Epsilon()
    A.append(e1)
    e1.pointsAt = B
    B.append(e2)
    e2.pointsAt = B
    assert set(E_set(A)) == {A, B}

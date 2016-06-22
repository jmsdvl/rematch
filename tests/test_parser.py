from string import ascii_letters, digits
import pytest

from rematch import (TreeNode, LiteralExpr, NullString, StarExpr, ChoiceExpr,
                    ConcatExpr, parse, level_first_walk)

CHARS = ascii_letters + digits


def test_parser_literal():
    for expr, char in zip(map(parse, CHARS), CHARS):
        assert isinstance(expr, LiteralExpr)
        assert expr.value == char


def test_parser_nullstring():
    expr = parse('')
    assert isinstance(expr, NullString)


def test_parse_star():
    expr = parse('a*')
    assert isinstance(expr, StarExpr)
    subexpr = expr.repetand
    assert isinstance(subexpr, LiteralExpr)
    assert subexpr.value == 'a'


def test_parse_choice():
    expr = parse('a|b')
    assert isinstance(expr, ChoiceExpr)
    left, right = expr
    assert isinstance(left, LiteralExpr)
    assert isinstance(right, LiteralExpr)
    assert left.value == 'a'
    assert right.value == 'b'


def test_parse_concat():
    expr = parse('ab')
    assert isinstance(expr, ConcatExpr)
    left, right = expr
    assert isinstance(left, LiteralExpr)
    assert isinstance(right, LiteralExpr)
    assert left.value == 'a'
    assert right.value == 'b'


def test_parse_plus():
    expr = parse('a+')
    assert isinstance(expr, ConcatExpr)
    left, right = expr
    assert isinstance(left, LiteralExpr)
    assert left.value == 'a'
    assert isinstance(right, StarExpr)
    right_subexpr = right.repetand
    assert isinstance(right_subexpr, LiteralExpr)
    assert right_subexpr.value == 'a'


def test_backslash_escapes():
    metachars = r'*?+.\()|'
    exprs = map(parse, (r'\*', r'\?', r'\+', r'\.',
                        r'\\', r'\(', r'\)', r'\|'))
    for expr, metachar in zip(exprs, metachars):
        assert isinstance(expr, LiteralExpr)
        assert expr.value == metachar


def test_complex_expression():
    toplevel = parse('ab*(c|d)?')
    assert isinstance(toplevel, ConcatExpr)
    left, right = toplevel

    assert isinstance(left, ConcatExpr)
    leftleft, leftright = left
    assert isinstance(leftleft, LiteralExpr)
    assert leftleft.value == 'a'
    assert isinstance(leftright, StarExpr)
    assert isinstance(leftright.repetand, LiteralExpr)
    assert leftright.repetand.value == 'b'

    assert isinstance(right, ChoiceExpr)
    rightleft, rightright = right
    assert isinstance(rightleft, ChoiceExpr)
    assert isinstance(rightright, NullString)
    rl_left, rl_right = rightleft
    assert isinstance(rl_left, LiteralExpr)
    assert rl_left.value == 'c'
    assert isinstance(rl_right, LiteralExpr)
    assert rl_right.value == 'd'


def test_nested_parens_resolved_correctly():
    expr = parse(r'(ab(a|d)e)')

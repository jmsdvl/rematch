import string
import pytest

from rematch import Regex


CHARS = string.ascii_letters + string.digits


def test_literal():
    matchers = [Regex(ch) for ch in CHARS]
    assert all(RE(ch) for RE, ch in zip(matchers, CHARS))
#    for RE in matchers:
#        assert not any(RE(ch) for ch in CHARS.replace(RE.pattern, ''))


def test_period_metacharacter():
    RE = Regex('.')
    assert all(RE(ch) for ch in CHARS)


def test_simple_concat():
    RE = Regex('ab')
    assert RE('ab')
    assert not RE('ba')
    assert not RE('a')
    assert not RE('b')


def test_concat_with_period_metacharacter():
    RE = Regex('a.b')
    for string in ('a{}b'.format(ch) for ch in CHARS):
        assert RE(string)
    assert not RE('ab')


def test_simple_alternation():
    RE = Regex('a|b')
    assert RE('a')
    assert RE('b')
    assert not RE('ab')


def test_simple_star():
    RE = Regex('a*')
    for i in range(0, 10):
        assert RE('a'*i)
    for i in range(10):
        assert not RE('b{}'.format('a'*i))
    assert not RE('aaaab')


def test_simple_escape():
    RE = Regex(r'\*test\?')
    assert RE(r'*test?')


def test_simple_question_mark():
    RE = Regex('a?')
    assert RE('a')
    assert RE('')


def test_parens():
    RE = Regex(r'a(b|d)')
    assert RE('ab')
    assert RE('ad')


def test_empty_re():
    RE = Regex('')
    assert RE('')
    assert not RE('a')


def test_plus_operator():
    RE = Regex('a+')
    assert RE('a')
    assert RE('aa')
    assert RE('aaaaaaaaaaaaaaaaaaaaaaaaaaa')
    assert not RE('')
    assert not RE('ba')


def test_outside_paren_star():
    RE = Regex('(a|b)*')
    for match in "ab aa bb abab abba baba".split():
        assert RE(match)


def test_pathological():
    pattern = 'a?'*30
    match = 'a'*29
    RE = Regex(pattern)
    assert RE(match)
    assert not RE(match + 'aa')

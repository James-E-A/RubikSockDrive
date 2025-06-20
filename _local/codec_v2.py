from .ranking import *
from .cube import Cube
from .multiset42 import Bag

from itertools import count
from math import comb
import sys

__all__ = ['bytes_to_cubes', 'cubes_to_bytes', 'str50_to_cubes', 'cubes_to_str50']


def bytes_to_cubes(s: bytes, *, t=Cube) -> 'Collection[Cube]':
    "Biject an octet string to a bag of Cubes."
    N = t.GROUP.order()  # 43_252_003_274_489_856_000
    x = octet_rank(s)
    cs = Bag()
    for j in _nat_to_nbag(x, N):
        cs.add(t(t.GROUP.coset_unrank(j)))
    return cs


def str50_to_cubes(s: str, *, t=Cube) -> 'Collection[Cube]':
    "Biject a string to a bag of Cubes. Extremely limited character support."
    N = t.GROUP.order()
    x = str50_rank(s)
    cs = Bag()
    for j in _nat_to_nbag(x, N):
        cs.add(t(t.GROUP.coset_unrank(j)))
    return cs


def cubes_to_bytes(cs: 'Collection[Cube]') -> bytes:
    "Inverse of `bytes_to_cubes`."
    if not cs: return b""
    t, = set(c.__class__ for c in cs)
    N = t.GROUP.order()  # 43_252_003_274_489_856_000
    js = ( t.GROUP.coset_rank(c._permutation) for c in cs )
    x = _nbag_to_nat(js, N)
    return octet_unrank(x)


def cubes_to_str50(cs: 'Collection[Cube]') -> str:
    "Inverse of `cubes_to_str50`."
    if not cs: return ""
    t, = set(c.__class__ for c in cs)
    N = t.GROUP.order()  # 43_252_003_274_489_856_000
    js = ( t.GROUP.coset_rank(c._permutation) for c in cs )
    x = _nbag_to_nat(js, N)
    return str50_unrank(x)


#typing: Natural = Annotated[int, lambda _: (0 <= _)]
#typing: NaturalLessThan[n] = Annotated[int, lambda _: (0 <= _ < n)]
#typing: FixedSizeSet[T, k] = Annotated[Set[T], lambda _: (len(_) == k)]


def _nat_to_nbag(x: 'Natural', n: 'Natural') -> 'Collection[NaturalLessThan[n]]':
    "Biject *x* from the natural numbers, to the set of all multisets of natural numbers which are less than *n*."
    if x == 0: return Bag()
    # 1. Calculate epoch (k) and offset (bias)
    bias = 1
    k = 1
    while not (x - bias) in range(multicomb(n, k)):
        bias += multicomb(n, k)
        k += 1

    # 2. Natural -> Combination
    s = _nat_to_kcomb(x - bias, k)

    # 3. Combination -> Multiset
    return Bag( (elem - i) for (i, elem) in enumerate(sorted(s)) )


def _nbag_to_nat(ms: 'Collection[NaturalLessThan[n]]', n: 'Natural') -> 'Natural':
    "Inverse of `_nat_to_nbag`."
    # 1. Multiset -> Combination
    s = set( (x + i) for (i, x) in enumerate(sorted(ms)) )

    # 2. Calculate offset
    bias = sum(multicomb(n, k) for k in range(len(s)))

    # 3. Combination -> Natural
    return _kcomb_to_nat(s) + bias


def _nat_to_kcomb(x: 'Natural', k: 'Natural') -> 'FixedSizeSet[Natural, k]':
    """https://en.wikipedia.org/wiki/Combinatorial_number_system#Finding_the_k-combination_for_a_given_number
    """
    x = int(x)
    if (x > 0) and not (k > 0):
        raise ValueError(f"can't represent {x} as a {k}-combination (k too small)")

    result = set()
    for i in reversed(range(k)):
        elem = _search_maxsatisfying(lambda n: not comb(n, i+1) > x)  # TODO performance
        assert elem not in result
        result.add(elem)
        x -= comb(elem, i+1)

    return result


def _kcomb_to_nat(s: 'Set[Natural]') -> 'Natural':
    """https://en.wikipedia.org/wiki/Combinatorial_number_system#Place_of_a_combination_in_the_ordering

    Inverse of ``_nat_to_kcomb``.
    """
    return sum(comb(elem, i+1) for i, elem in enumerate(sorted(s)))


def multicomb(n: 'Natural', k: 'Natural') -> 'Natural':
    """https://en.wikipedia.org/wiki/Multiset_coefficient
    """
    return comb((n + k - 1), k)


def _search_maxsatisfying(predicate: 'Callable[[T], bool]', *, start: int=0, _increasefunc: 'Callable[[int], int]'=lambda n, _base=sys.maxsize+1: n*_base):
    """Return the largest integer *n* for which predicate(n) succeeds

    predicate must have a nowhere-positive derivative.
    start value must satisfy predicate."""
    if start < 0:
        offset = -start
        return search_maxsatisfying(lambda guess: predicate(guess - offset), start=0, _increasefunc=_increasefunc) - offset
    lower_bound = start
    upper_bound = lower_bound + 1
    if not predicate(lower_bound):
        raise ValueError("start value does not satisfy predicate")

    # 1. Exponential approach to establish upper-bound
    while predicate(upper_bound):
        lower_bound, upper_bound = upper_bound, _increasefunc(upper_bound)
    guess = lower_bound

    # 2. Binary search
    while (upper_bound - lower_bound) > 1:
        guess = lower_bound + (upper_bound - lower_bound) // 2
        if not predicate(guess):
            upper_bound = guess
            guess = lower_bound
        else:
            lower_bound = guess

    assert predicate(guess) and not predicate(guess+1)
    return guess

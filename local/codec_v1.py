from .ranking import *
from .cube import Cube

__all__ = ['bytes_to_cube', 'cube_to_bytes']


def bytes_to_cube(s):
    i = octet_rank(s)
    p = _Cube.GROUP.coset_unrank(i)
    c = _Cube(p)
    return c

def cube_to_bytes(c):
    p = c._permutation
    c = _Cube.GROUP.coset_rank(p)
    s = octet_unrank(c)
    return s

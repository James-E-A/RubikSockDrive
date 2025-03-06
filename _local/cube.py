import sympy.combinatorics  # python -m pip install "sympy >= 0.7.2"
import kociemba as _kociemba  # python -m pip install "kociemba >= 1.2"

import re


class Cube:
    """Immutable class representing a Rubik's Cube.

    May represent "illegal" states.
    """
    __slots__ = ['__impl', '_hash']

    @classmethod
    def random_cube(cls):
        p = cls.GROUP.random()
        return cls(p)

    _COLORS = (15, 10, 9, 4, 3, 11)  # Override this to re-color a subclass! JP -> (15, 10, 4, 11, 3, 4)
    _COLOR_LETTERS = ('w', 'g', 'r', 'b', 'o', 'y')
    _COLOR_INDICES = (
        0, 0, 0,
        0, 0, 0,
        0, 0, 0,

        1, 1, 1,  2, 2, 2,  3, 3, 3,  4, 4, 4,
        1, 1, 1,  2, 2, 2,  3, 3, 3,  4, 4, 4,
        1, 1, 1,  2, 2, 2,  3, 3, 3,  4, 4, 4,

        5, 5, 5,
        5, 5, 5,
        5, 5, 5,
    )

    _ANSI_REPR_EXTRA = (
        '# \x1b[0m\x1b[8m\u2591\u2591\u2591\x1b[0m \x1b[38;5;\ue500m\x1b[48;5;\ue503m\u2580\x1b[38;5;\ue501m\x1b[48;5;\ue504m\u2580\x1b[38;5;\ue502m\x1b[48;5;\ue505m\u2580\x1b[0m \x1b[8m\u2591\x1b[0m\n'
        '# \x1b[8m\u2591\u2591\u2591\x1b[0m \x1b[38;5;\ue506m\u2580\x1b[38;5;\ue507m\u2580\x1b[38;5;\ue508m\u2580\x1b[0m\n'
        '# \x1b[38;5;\ue512m\x1b[48;5;\ue51em\u2580\x1b[38;5;\ue513m\x1b[48;5;\ue51fm\u2580\x1b[38;5;\ue514m\x1b[48;5;\ue520m\u2580\x1b[0m \x1b[38;5;\ue509m\x1b[48;5;\ue515m\u2580\x1b[38;5;\ue50am\x1b[48;5;\ue516m\u2580\x1b[38;5;\ue50bm\x1b[48;5;\ue517m\u2580\x1b[0m \x1b[38;5;\ue50cm\x1b[48;5;\ue518m\u2580\x1b[38;5;\ue50dm\x1b[48;5;\ue519m\u2580\x1b[38;5;\ue50em\x1b[48;5;\ue51am\u2580\x1b[0m \x1b[38;5;\ue50fm\x1b[48;5;\ue51bm\u2580\x1b[38;5;\ue510m\x1b[48;5;\ue51cm\u2580\x1b[38;5;\ue511m\x1b[48;5;\ue51dm\u2580\x1b[0m \x1b[8m\u2591\x1b[0m\n'
        '# \x1b[38;5;\ue52am\u2580\x1b[38;5;\ue52bm\u2580\x1b[38;5;\ue52cm\u2580\x1b[0m \x1b[38;5;\ue521m\u2580\x1b[38;5;\ue522m\u2580\x1b[38;5;\ue523m\u2580\x1b[0m \x1b[38;5;\ue524m\u2580\x1b[38;5;\ue525m\u2580\x1b[38;5;\ue526m\u2580\x1b[0m \x1b[38;5;\ue527m\u2580\x1b[38;5;\ue528m\u2580\x1b[38;5;\ue529m\u2580\x1b[0m\n'
        '# \x1b[8m\u2591\u2591\u2591\x1b[0m \x1b[38;5;\ue52dm\x1b[48;5;\ue530m\u2580\x1b[38;5;\ue52em\x1b[48;5;\ue531m\u2580\x1b[38;5;\ue52fm\x1b[48;5;\ue532m\u2580\x1b[0m \x1b[8m\u2591\x1b[0m\n'
        '# \x1b[8m\u2591\u2591\u2591\x1b[0m \x1b[38;5;\ue533m\u2580\x1b[38;5;\ue534m\u2580\x1b[38;5;\ue535m\u2580\x1b[0m'
    )
    _ANSI_REPR_EXTRA_RE5 = re.compile(r'[\uE500-\uE535]')

    def __hash__(self):
        if self._hash is None:
            self._hash = hash( (self._permutation, frozenset(frozenset(piece) for piece in self.POLYHEDRON_FACES), self.GROUP))
        return self._hash

    def __repr__(self):
        stickers = [self._COLORS[self._COLOR_INDICES[i]] for i in self.__impl]
        solution = [self.MOVES[m] for m in _kociemba.solve(self._alt_str('github.com/muodov/kociemba')).split()]
        creation_str = ' '.join(_dindex(self.MOVES, ~m) for m in reversed(solution))

        return (
            f"{self.__class__.__name__}({str(self)!r})\n"
            f"{re.sub(self._ANSI_REPR_EXTRA_RE5, lambda m: str(stickers[ord(m.group(0)) - 0xE500]), self._ANSI_REPR_EXTRA)}\n"
            f"# {creation_str}\n"
        )

    MOVES = {
        'U': sympy.combinatorics.Permutation(53)( 0,  6,  8,  2)( 1,  3,  7,  5)( 9, 12, 15, 18)(10, 13, 16, 19)(11, 14, 17, 20),
        'F': sympy.combinatorics.Permutation(53)( 6, 44, 47, 12)( 7, 32, 46, 24)( 8, 20, 45, 36)( 9, 33, 35, 11)(10, 21, 34, 23),
        'R': sympy.combinatorics.Permutation(53)( 2, 11, 47, 39)( 5, 23, 50, 27)( 8, 35, 53, 15)(12, 36, 38, 14)(13, 24, 37, 26),
        'B': sympy.combinatorics.Permutation(53)( 0, 14, 53, 42)( 1, 26, 52, 30)( 2, 38, 51, 18)(15, 39, 41, 17)(16, 27, 40, 29),
        'L': sympy.combinatorics.Permutation(53)( 0, 41, 45,  9)( 3, 29, 48, 21)( 6, 17, 51, 33)(18, 42, 44, 20)(19, 30, 43, 32),
        'D': sympy.combinatorics.Permutation(53)(33, 42, 39, 36)(34, 43, 40, 37)(35, 44, 41, 38)(45, 51, 53, 47)(46, 48, 52, 50),
    }

    GROUP = sympy.combinatorics.PermutationGroup(*MOVES.values())

    POLYHEDRON_FACES = [
        (1, 16), (3, 19), (5, 13), (7, 10), (21, 32), (23, 24), (26, 27), (29, 30), (34, 46), (37, 50), (40, 52), (43, 48),
        (0, 18, 17), (2, 15, 14), (6, 9, 20), (8, 12, 11), (33, 45, 44), (35, 36, 47), (38, 39, 53), (41, 42, 51),
        (4,), (22,), (25,), (28,), (31,), (49,),
    ]

    MOVES['U2'] = MOVES['U']**2
    MOVES['F2'] = MOVES['F']**2
    MOVES['R2'] = MOVES['R']**2
    MOVES['B2'] = MOVES['B']**2
    MOVES['L2'] = MOVES['L']**2
    MOVES['D2'] = MOVES['D']**2

    MOVES["U'"] = MOVES['U']**3
    MOVES["F'"] = MOVES['F']**3
    MOVES["R'"] = MOVES['R']**3
    MOVES["B'"] = MOVES['B']**3
    MOVES["L'"] = MOVES['L']**3
    MOVES["D'"] = MOVES['D']**3

    @classmethod
    def _solverstring_to_permutation(cls, s):
        stickers = [cls._COLOR_LETTERS.index(c) for c in s]
        p = [None] * cls.GROUP.degree

        _colormap = {
            # Mapping from SETS of sticker colors
            frozenset(cls._COLOR_INDICES[i] for i in piece):
            # to (Mapping from INDIVIDUAL sticker colors to sticker positions)
            {cls._COLOR_INDICES[i]: i for i in piece}
          for piece in cls.POLYHEDRON_FACES
        }

        for cur_piece in cls.POLYHEDRON_FACES:
            # First, we pick some piece (SAY the Front-Up edge)...
            # ...and figure out what the hell actually landed in it.
            cur_colors = {cls._COLOR_LETTERS.index(s[i]) for i in cur_piece}
            # then, we figure out where these stickers that HAVE landed in our piece
            # came from originally
            src_colormap = _colormap[frozenset(cur_colors)]
            # then we record exactly where each of our stickers came from
            for cur_index in cur_piece:
                cur_color = cls._COLOR_LETTERS.index(s[cur_index])
                assert p[cur_index] is None
                p[cur_index] = src_colormap[cur_color]
        assert None not in p

        return sympy.combinatorics.Permutation(p)

    @property
    def _permutation(self):
        return self.__impl

    def _alt_str(self, version):
        if version == 'rubiks-cube-solver.com':
            p_mod = sympy.combinatorics.Permutation(53)(9, 18)(10, 19)(11, 20)(12, 30, 24, 33, 36, 15, 42, 39, 27)(13, 31, 25, 34, 37, 16, 43, 40, 28)(14, 32, 26, 35, 38, 17, 44, 41, 29)
            p = p_mod * self._permutation
            color_letters = ('1', '3', '4', '5', '2', '6')
            return f'https://rubiks-cube-solver.com/solution.php?cube=0{"".join(color_letters[self._COLOR_INDICES[i]] for i in p)}'
        elif version == 'github.com/muodov/kociemba':
            p_mod = sympy.combinatorics.Permutation(53)(9, 12, 24, 33, 51, 39, 30, 48, 27, 45, 15, 36, 18)(10, 13, 25, 34, 52, 40, 31, 49, 28, 46, 16, 37, 19)(11, 14, 26, 35, 53, 41, 32, 50, 29, 47, 17, 38, 20)
            p = p_mod * self._permutation
            color_letters = ('U', 'F', 'R', 'B', 'L', 'D')
            return ''.join(color_letters[self._COLOR_INDICES[i]] for i in p)
        raise ValueError(version)

    def __str__(self):
        return ''.join(self._COLOR_LETTERS[self._COLOR_INDICES[sticker_number]] for sticker_number in self.__impl)

    def __init__(self, initializer=None):
        if initializer is None:
            p = self.GROUP.identity
        elif isinstance(initializer, str):
            p = self._solverstring_to_permutation(initializer)
        elif isinstance(initializer, sympy.combinatorics.Permutation):
            assert initializer in self.GROUP
            p = initializer
        elif isinstance(initializer, int):
            p = self.GROUP.coset_unrank(initializer)
        else:
            raise TypeError(f'Non-Implemented Cube initializer type: {type(initializer)}')
        self.__impl = p
        self._hash = None

    def __eq__(self, other):
        if not isinstance(other, Cube):
            return NotImplemented
        return (self.GROUP, self._permutation) == (other.GROUP, other._permutation)


def _dindex(d, x):
    try:
        return next(k for k,v in d.items() if v == x)
    except StopIteration:
        raise ValueError(x)
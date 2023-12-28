import sympy.combinatorics  # python -m pip install sympy


class Cube:
    """Immutable class representing a Rubik's Cube.

    May represent "illegal" states.
    """
    __slots__ = ['__impl', '_hash']

    @classmethod
    def random_cube(cls):
        p = cls.GROUP.random()
        return cls(p)

    _COLORS = (15, 10, 1, 4, 3, 11)  # Override this to re-color a subclass!
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

    def __hash__(self):
        if self._hash is None:
            self._hash = hash( (self._permutation, frozenset(frozenset(piece) for piece in self.POLYHEDRON_FACES), self.GROUP))
        return self._hash

    def __repr__(self):
        stickers = [self._COLORS[self._COLOR_INDICES[i]] for i in self.__impl]
        solverstring = ''.join(self._COLOR_LETTERS[self._COLOR_INDICES[i]] for i in self.__impl)
        #if inspect.stack()[1].filename != '<stdin>':
        #    # https://stackoverflow.com/questions/77719065
        #    return f'{self.__class__.__name__}({solverstring!r})'
        return (
            f'{self.__class__.__name__}({solverstring!r})'  # (actual repr)
            '\n# '
            '\x1b[0m\x1b[8m\u2591\u2591\u2591\x1b[0m '  # (indent)
            '\x1b[38;5;{stickers[0]}m\x1b[48;5;{stickers[3]}m\u2580\x1b[38;5;{stickers[1]}m\x1b[48;5;{stickers[4]}m\u2580\x1b[38;5;{stickers[2]}m\x1b[48;5;{stickers[5]}m\u2580'  # U (top 2 rows)
            '\x1b[0m'
            '\n# '
            '\x1b[8m\u2591\u2591\u2591\x1b[0m '  # (indent)
            '\x1b[38;5;{stickers[6]}m\u2580\x1b[38;5;{stickers[7]}m\u2580\x1b[38;5;{stickers[8]}m\u2580'  # U (bottom row)
            '\x1b[0m'
            '\n# '
            '\x1b[38;5;{stickers[18]}m\x1b[48;5;{stickers[30]}m\u2580\x1b[38;5;{stickers[19]}m\x1b[48;5;{stickers[31]}m\u2580\x1b[38;5;{stickers[20]}m\x1b[48;5;{stickers[32]}m\u2580'  # L (top 2 rows)
            '\x1b[0m '
            '\x1b[38;5;{stickers[9]}m\x1b[48;5;{stickers[21]}m\u2580\x1b[38;5;{stickers[10]}m\x1b[48;5;{stickers[22]}m\u2580\x1b[38;5;{stickers[11]}m\x1b[48;5;{stickers[23]}m\u2580'  # F (top 2 rows)
            '\x1b[0m '
            '\x1b[38;5;{stickers[12]}m\x1b[48;5;{stickers[24]}m\u2580\x1b[38;5;{stickers[13]}m\x1b[48;5;{stickers[25]}m\u2580\x1b[38;5;{stickers[14]}m\x1b[48;5;{stickers[26]}m\u2580'  # R (top 2 rows)
            '\x1b[0m '
            '\x1b[38;5;{stickers[15]}m\x1b[48;5;{stickers[27]}m\u2580\x1b[38;5;{stickers[16]}m\x1b[48;5;{stickers[28]}m\u2580\x1b[38;5;{stickers[17]}m\x1b[48;5;{stickers[29]}m\u2580'  # B (top 2 rows)
            '\x1b[0m'
            '\n# '
            '\x1b[38;5;{stickers[42]}m\u2580\x1b[38;5;{stickers[43]}m\u2580\x1b[38;5;{stickers[44]}m\u2580'  # L (bottom row)
            '\x1b[0m '
            '\x1b[38;5;{stickers[33]}m\u2580\x1b[38;5;{stickers[34]}m\u2580\x1b[38;5;{stickers[35]}m\u2580'  # F (bottom row)
            '\x1b[0m '
            '\x1b[38;5;{stickers[36]}m\u2580\x1b[38;5;{stickers[37]}m\u2580\x1b[38;5;{stickers[38]}m\u2580'  # R (bottom row)
            '\x1b[0m '
            '\x1b[38;5;{stickers[39]}m\u2580\x1b[38;5;{stickers[40]}m\u2580\x1b[38;5;{stickers[41]}m\u2580'  # B (bottom row)
            '\x1b[0m'
            '\n# '
            '\x1b[8m\u2591\u2591\u2591\x1b[0m '  # (indent)
            '\x1b[38;5;{stickers[45]}m\x1b[48;5;{stickers[48]}m\u2580\x1b[38;5;{stickers[46]}m\x1b[48;5;{stickers[49]}m\u2580\x1b[38;5;{stickers[47]}m\x1b[48;5;{stickers[50]}m\u2580'  # D (top 2 rows)
            '\x1b[0m'
            '\n# '
            '\x1b[8m\u2591\u2591\u2591\x1b[0m '  # (indent)
            '\x1b[38;5;{stickers[51]}m\u2580\x1b[38;5;{stickers[52]}m\u2580\x1b[38;5;{stickers[53]}m\u2580'  # D (bottom row)
            '\x1b[0m'
            '\n'
        ).format(stickers=stickers, solverstring=solverstring)

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

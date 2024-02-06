from sortedcontainers import SortedDict  # python -m pip install sortedcontainers

from collections import Counter
from collections.abc import Hashable, Mapping
from itertools import chain, repeat, starmap
from math import isqrt
from numbers import Real
import warnings


class Multiset:
    __slots__ = ['__impl']

    @classmethod
    def _key(cls, obj):
        if isinstance(obj, Real):
            return (0, obj)
        elif isinstance(obj, tuple):
            return (1, tuple(map(cls._key, obj)))
        elif isinstance(obj, Hashable):
            return (2, hash(obj))
        else:
            return (3, id(obj))

    def __init__(self, iterable_or_collection=None):
        self.__impl = SortedDict(self._key)

        if iterable_or_collection is not None:
            if isinstance(iterable_or_collection, Mapping):
                warnings.warn('Did you mean Multiset.fromcounter()?')
            for elem in iterable_or_collection:
                self.add(elem)

    @classmethod
    def fromcounter(cls, counter):
        self = cls()
        for elem, count in counter.items():
            self.add(elem, _count=count)
        return self

    def count(self, elem):
        return self.__impl.get(elem, 0)

    def __repr__(self):
        if not self:
            return f'{self.__class__.__name__}()'
        if isqrt(len(self)) > self.support_len():
            # Alternate repr when multiplicity is EXCESSIVE
            d = dict(self.__impl)
            return f'{self.__class__.__name__}.fromcounter({d!r})'
        l = list(self)
        return f'{self.__class__.__name__}({l!r})'

    def __contains__(self, elem):
        return elem in self.__impl

    def support(self):
        return set(self.__impl.keys())

    def support_len(self):
        return len(self.__impl.keys())

    def __len__(self):
        return sum(self.__impl.values())

    def __iter__(self):
        items = self.__impl.items()
        yield from chain.from_iterable(starmap(repeat, items))

    def __bool__(self):
        return bool(self.__impl)

    def add(self, elem, *, _count=1):
        assert isinstance(_count, int) and _count > 0
        cur_count = self.__impl.get(elem, 0)
        self.__impl[elem] = cur_count + _count

    def remove(self, elem, *, _count=1):
        assert isinstance(_count, int) and _count > 0
        cur_count = self.__impl.get(elem, 0)
        if cur_count == 0:
            raise KeyError(elem)
        assert cur_count >= _count
        if cur_count == _count:
            del self.__impl[elem]
        else:
            self.__impl[elem] = cur_count - _count

    def discard(self, elem):
        if elem in self.__impl:
            del self.__impl[elem]

    def pop(self):
        if not self:
            raise KeyError('pop from an empty Multiset')
        elem = next(reversed(self.__impl))
        self.remove(elem)
        return elem

    def clear(self):
        self.__impl.clear()

    def __add__(self, other):
        if not isinstance(other, Multiset):
            return NotImplemented
        raise NotImplementedError('Multiset.__add__ TODO')

    def __sub__(self, other):
        if not isinstance(other, Multiset):
            return NotImplemented
        raise NotImplementedError('Multiset.__sub__ TODO')

    def __and__(self, other):
        if not isinstance(other, Multiset):
            return NotImplemented
        raise NotImplementedError('Multiset.__and__ TODO')

    def __or__(self, other):
        if not isinstance(other, Multiset):
            return NotImplemented
        raise NotImplementedError('Multiset.__or__ TODO')

    def __xor__(self, other):
        if not isinstance(other, Multiset):
            return NotImplemented
        raise NotImplementedError('Multiset.__xor__ TODO')

    def isdisjoint(self, other):
        if not isinstance(other, Multiset):
            raise TypeError(f'Multiset.isdisjoint: expected Multiset, got {type(other)}')
        raise NotImplementedError('Multiset.isdisjoint TODO')

    def __le___(self, other):
        if not isinstance(other, Multiset):
            return NotImplemented
        raise NotImplementedError('Multiset.__le__ TODO')

    def __lt___(self, other):
        if not isinstance(other, Multiset):
            return NotImplemented
        raise NotImplementedError('Multiset.__lt__ TODO')

    def __ge___(self, other):
        if not isinstance(other, Multiset):
            return NotImplemented
        raise NotImplementedError('Multiset.__ge__ TODO')

    def __gt___(self, other):
        if not isinstance(other, Multiset):
            return NotImplemented
        raise NotImplementedError('Multiset.__gt__ TODO')

    def __eq__(self, other):
        if not isinstance(other, Multiset):
            return NotImplemented
        return self.__impl == other.__impl

    def __ne__(self, other):
        if not isinstance(other, Multiset):
            return NotImplemented
        return self.__impl != other.__impl

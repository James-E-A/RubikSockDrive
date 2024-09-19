"""Multiset implementation.

"""

__all__ = ['Multiset', 'FrozenMultiset']

from collections import Counter
from collections.abc import Iterable, KeysView, Mapping, MutableSet, Set
from functools import total_ordering
from itertools import chain, repeat, starmap
import logging
from math import isqrt


class _MultisetBase:
    __slots__ = ['__impl']

    def __repr__(self):
        if not self:
            return f'{self.__class__.__name__}()'
        if isqrt(self.__len__()) > len(self.support()):
            # Special repr for Multisets with high multiplicity factor
            # - e.g. Multiset.fromcounts({1: 4}) instead of Multiset([1, 1, 1, 1])
            # - e.g. Multiset.fromcounts({42: 10**100}) instead of Multiset([�])
            return f'{self.__class__.__name__}.fromcounts({self.__impl!r})'
        # Case default
        return f'{self.__class__.__name__}({list(self)!r})'

    def __contains__(self, elem):
        return elem in self.__impl.keys()

    def __iter__(self):
        yield from chain.from_iterable(starmap(repeat, self.__impl.items()))

    def __len__(self):
        # returns the cardinality of the Multiset itself.
        # for the cardinality of the support of the Multiset, use len(_.support()) instead.
        return sum(self.__impl.values())

    def count(self, elem):
        return self.__impl.get(elem, 0)

    def __init__(self, iterable=()):
        self.__impl = dict()
        if isinstance(iterable, _MultisetBase):
            self.__impl.update(iterable.__impl)
            return
        if isinstance(iterable, Mapping):
            if isinstance(iterable, Counter):
                logging.warning(DeprecationWarning("Counter passed to Multiset() constructor\nThis behavior is deprecated; call Multiset.fromcounts(items_or_mapping) instead."))
                self.__impl.update(iterable)
                return
            else:
                logging.warning(RuntimeWarning("Mapping passed to Multiset() constructor\nIf you really meant to create a Multiset with just 1 of each key, explicitly call Multiset(mapping.keys()) to suppress this warning; if you meant to create a Multiset initialized with element-quantity pairs, call Multiset.fromcounts(items_or_mapping) instead."))
        for elem in iterable:
            _MultisetBase.add(self, elem) # call class method directly to avoid breaking when mutation methods are masked in subclass

    def copy(self):
        result = self.__class__()
        result.__impl.update(self.__impl)
        return result

    @classmethod
    def fromcounts(cls, items_or_mapping):
        self = cls()
        if isinstance(items_or_mapping, Mapping):
            items = items_or_mapping.items()
        else:
            items = items_or_mapping
        for elem, qty in items:
            _MultisetBase.add(self, elem, qty) # call class method directly to avoid breaking when mutation methods are masked in subclass
        return self

    def extend(self, other):
        if not isinstance(other, _MultisetBase):
            other = Multiset(other)
        self += other

    def update(self, *others):
        for other in others:
            if not isinstance(other, _MultisetBase):
                other = Multiset(other)
            self |= other

    def intersection_update(self, *others):
        for other in others:
            if not isinstance(other, _MultisetBase):
                other = Multiset(other)
            self &= other

    def difference_update(self, *others):
        for other in others:
            if not isinstance(other, _MultisetBase):
                other = Multiset(other)
            self -= other

    def symmetric_difference_update(self, other):
        if not isinstance(other, _MultisetBase):
            other = Multiset(other)
        self ^= other

    def isdisjoint(self, other):
        if not isinstance(other, _MultisetBase):
            other = Multiset(other)
        return self.support().isdisjoint(other.support())

    def issubset(self, other):
        if not isinstance(other, _MultisetBase):
            other = Multiset(other)
        return self <= other

    def issuperset(self, other):
        if not isinstance(other, _MultisetBase):
            other = Multiset(other)
        return self <= other

    def _set(self, elem, count):
        assert isinstance(count, int) and count >= 0
        if count:
            self.__impl[elem] = count
        else:
            self.__impl.pop(elem, None)

    def add(self, elem, _count=1):
        if not isinstance(_count, int):
            raise TypeError
        if not _count >= 0:
            raise ValueError(_count)
        self._set(elem, self.count(elem) + _count)

    def remove(self, elem, _count=1):
        if not isinstance(_count, int):
            raise TypeError
        if not _count >= 0:
            raise ValueError(_count)
        cur = self.count(elem)
        result = cur - _count
        if not result >= 0:
            if not cur:
                # qualitative issue
                raise KeyError(elem)
            else:
                # quantitative issue
                raise ValueError(f"{self!r} does not contain {elem!r} with {_count} multiplicity.\nIf you meant to remove all of that element, use .discard(elem)")
        self._set(elem, result)

    def discard(self, elem):
        self.__impl.pop(elem, None)

    def clear(self):
        self.__impl.clear()

    def pop(self):
        try:
            elem = next(reversed(self.__impl.keys()))
        except StopIteration:
            raise KeyError('pop from an empty set') from None
        else:
            self.remove(elem, 1)
            return elem

    def union(self, *others):
        result = self.copy()
        result.union_update(*others)
        return result

    def intersection(self, *others):
        result = self.copy()
        result.intersection_update(*others)
        return result

    def difference(self, *others):
        result = self.copy()
        result.difference_update(*others)
        return result

    def symmetric_difference(self, *others):
        result = self.copy()
        result.symmetric_difference_update(*others)
        return result

    def __bool__(self):
        return bool(self.__impl)

    def support(self):
        return _MultisetSupportView(self.__impl)

    @property
    def _mapping(self):
        return self.__impl

    def __le__(self, other):
        if not isinstance(other, _MultisetBase):
            if isinstance(other, Set):
                other = Multiset(other)
            else:
                return NotImplemented
        if not len(self.support()) <= len(other.support()):
            return False
        other_impl_get = other.__impl.get
        return all(v <= other_impl_get(k, 0) for k, v in self.__impl.items())

    def __lt__(self, other):
        if not isinstance(other, _MultisetBase):
            if isinstance(other, Set):
                other = Multiset(other)
            else:
                return NotImplemented
        return self <= other and self != other

    def __eq__(self, other):
        if not isinstance(other, _MultisetBase):
            if isinstance(other, Set):
                other = Multiset(other)
            else:
                return NotImplemented
        return self.__impl == other.__impl

    def __ne__(self, other):
        if not isinstance(other, _MultisetBase):
            if isinstance(other, Set):
                other = Multiset(other)
            else:
                return NotImplemented
        return self.__impl != other.__impl

    def __gt__(self, other):
        if not isinstance(other, _MultisetBase):
            if isinstance(other, Set):
                other = Multiset(other)
            else:
                return NotImplemented
        return self >= other and self != other

    def __ge__(self, other):
        if not isinstance(other, _MultisetBase):
            if isinstance(other, Set):
                other = Multiset(other)
            else:
                return NotImplemented
        if not self.support_len() >= other.support_len():
            return False
        self_impl_get = self.__impl.get
        return all(self_impl_get(k, 0) >= v for k, v in other.__impl.items())

    def __and__(self, other):
        if not isinstance(other, _MultisetBase):
            if isinstance(other, Set):
                other = Multiset(other)
            else:
                return NotImplemented
        other_impl_get = other.__impl.get
        return self.__class__.fromcounts((k, min(v, other_impl_get(k, 0))) for k, v in self.__impl.items())

    def __or__(self, other):
        if not isinstance(other, _MultisetBase):
            if isinstance(other, Set):
                other = Multiset(other)
            else:
                return NotImplemented
        self_impl_get = self.__impl.get
        other_impl_get = other.__impl.get
        return self.__class__.fromcounts((k, max(self_impl_get(k, 0), other_impl_get(k, 0))) for k in set(chain(self.__impl.keys(), other.__impl.keys())))

    def __sub__(self, other):
        if not isinstance(other, _MultisetBase):
            if isinstance(other, Set):
                other = Multiset(other)
            else:
                return NotImplemented
        other_impl_get = other.__impl.get
        return self.__class__.fromcounts((k, max(0, v - other_impl_get(k, 0))) for k, v in self.__impl.items())

    def __xor__(self, other):
        if not isinstance(other, _MultisetBase):
            if isinstance(other, Set):
                other = Multiset(other)
            else:
                return NotImplemented
        self_impl_get = self.__impl.get
        other_impl_get = other.__impl.get
        return self.__class__.fromcounts((k, abs(self_impl_get(k, 0) - other_impl_get(k, 0))) for k in set(chain(self.__impl.keys(), other.__impl.keys())))

    def __add__(self, other):
        if not isinstance(other, _MultisetBase):
            if isinstance(other, Set):
                other = Multiset(other)
            else:
                return NotImplemented
        self_impl_get = self.__impl.get
        other_impl_get = other.__impl.get
        return self.__class__.fromcounts((k, self_impl_get(k, 0) + other_impl_get(k, 0)) for k in set(chain(self.__impl.keys(), other.__impl.keys())))

    
class _MultisetSupportView(KeysView):
    # https://github.com/python/cpython/blob/v3.12.5/Lib/_collections_abc.py#L857
    pass


class Multiset(_MultisetBase, MutableSet):
    """Multiset is a finite, unordered container with multiplicitous elements.

    It support every method that Python's set does, and also includes:
     - count() for list-count-like functionality in constant time
     - extend() for list-iadd-like functionality
     - support() for a View of the underlying support set
     
    """

    def __ior__(self, other):
        if not isinstance(other, _MultisetBase):
            if isinstance(other, Set):
                other = Multiset(other)
            else:
                return NotImplemented
        self_impl_get = self._mapping.get
        self_set = self._set
        for k, v in list(other._mapping.items()):
            self_set(k, max(self_impl_get(k, 0), v))
        return self

    def __iand__(self, other):
        if not isinstance(other, _MultisetBase):
            if isinstance(other, Set):
                other = Multiset(other)
            else:
                return NotImplemented
        other_impl_get = other._mapping.get
        self_set = self._set
        for k, v in list(self._mapping.items()):
            self_set(k, min(v, other_impl_get(k, 0)))
        return self

    def __ixor__(self, other):
        if not isinstance(other, _MultisetBase):
            if isinstance(other, Set):
                other = Multiset(other)
            else:
                return NotImplemented
        self_impl_get = self._mapping.get
        other_impl_get = other._mapping.get
        self_set = self._set
        for k in set(chain(self._mapping.keys(), other._mapping.keys())):
            self_set(k, abs(self_impl_get(k, 0) - other_impl_get(k, 0)))
        return self

    def __isub__(self, other):
        if not isinstance(other, _MultisetBase):
            if isinstance(other, Set):
                other = Multiset(other)
            else:
                return NotImplemented
        self_impl_get = self._mapping.get
        other_impl_get = other._mapping.get
        self_set = self._set
        for k in set(chain(self.support(), other.support())):
            self_set(k, max(0, self_impl_get(k, 0) - other_impl_get(k, 0)))
        return self

    def __iadd__(self, other):
        if not isinstance(other, _MultisetBase):
            if isinstance(other, Set):
                other = Multiset(other)
            else:
                return NotImplemented
        self_impl_get = self._mapping.get
        self_set = self._set
        for k, v in list(other._mapping.items()):
            self_set(k, self_impl_get(k, 0) + v)
        return self


class FrozenMultiset(_MultisetBase, Set):
    """Multiset is a finite, unordered, immutable container with multiplicitous elements.
    """
    __slots__ = ['_hash']
    def __init__(self, collection=()):
        super().__init__(collection)
        self._hash = None
    def __hash__(self):
        if self._hash is None:
            self._hash = Set._hash(self._mapping.items())
        return self._hash

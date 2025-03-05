"""Multiset implementation.

"""

__all__ = ['Bag', 'FrozenBag']

import collections
from collections.abc import Collection, Iterable, KeysView, Mapping, MutableSet, Set
from itertools import chain, repeat, starmap
from math import isqrt


class _MultisetBase:
    __slots__ = ('__impl',) # a mapping from elements to strictly positive integers

    # flagship methods

    def __init__(self, collection_or_counter=None):
        self.__impl = {} 
        if collection_or_counter:
            if isinstance(collection_or_counter, Mapping):

                if isinstance(collection_or_counter, _MultisetBase):
                    self.__impl.update(collection_or_counter.multiplicities())

                elif isinstance(collection_or_counter, collections.Counter):
                    self._update(collection_or_counter)

                else:
                    raise TypeError(f"Calling {self.__class__.__name__}() on a generic Mapping is ambiguous. Use {self.__class__.__name__}.fromelements() or {self.__class__.__name__}.fromcounts() instead.")

            elif isinstance(collection_or_counter, Iterable):
                self._extend(collection_or_counter)

            else:
                raise TypeError(f"initializer must be a Multiset, collections.Counter, or non-Mapping Set; got {collection_or_counter.__class__}")

    def __repr__(self):
        # empty repr
        if not self:
            return f'{self.__class__.__name__}()'

        # sepecial high-multiplicity repr
        if isqrt(self.__len__()) > len(self.support()):
            # - e.g. Bag.fromcounts({1: 4}) instead of Bag([1, 1, 1, 1])
            # - e.g. Bag.fromcounts({42: 10**100}) instead of Bag([�])
            return f'{self.__class__.__name__}.fromcounts({self.__impl!r})'

        # default repr
        return f'{self.__class__.__name__}({list(self)!r})'

    def __reduce__(self):
        return (self.__class__, (collections.Counter(self.__impl),))

    @classmethod
    def fromcounts(cls, counts):
        result = cls()
        result._update(counts)
        return result

    @classmethod
    def fromelements(cls, collection):
        result = cls()
        result._extend(collection, counter_as_plain_iterable=True)
        return result

    # Set-like methods

    def copy(self):
        return self.__class__.fromcounts(self.multiplicities())

    def __contains__(self, elem):
        return elem in self.__impl.keys()

    def __iter__(self):
        yield from chain.from_iterable(starmap(repeat, self.__impl.items()))

    def __len__(self):
        # returns the cardinality of the Multiset itself.
        # for the cardinality of the support of the Multiset, use len(_.support()) instead.
        return sum(self.__impl.values())

    def isdisjoint(self, other):
        a = self.support()
        b = other.support()
        return not any(elem in a for elem in b)

    def symmetric_difference(self, other):
        a = set(chain(self.support(), other.support()))
        self_count = self.count
        other_count = other.count
        return Bag((elem, count) for count in (abs(self_count(elem) - other_count(elem)) for elem in a) if count > 0)

    # unique Multiset methods

    def support(self):
        return _BagSupportSetView(self.__impl)

    def multiplicities(self):
        return self.__impl.items()

    # List methods

    def count(self, elem):
        return self.__impl.get(elem, 0)

    # Private mutation methods

    def _extend(self, collection, *, counter_as_plain_iterable=False):
        if isinstance(collection, _MultisetBase):
            self._sum_update(collection.multiplicities())
        elif isinstance(collection, collections.Counter) and not counter_as_plain_iterable:
            self._sum_update(collection)
        else:
            self._sum_update((elem, 1) for elem in collection)

    def _add(self, elem, count=1):
        self._sum_update([(elem, count)])

    def _remove(self, elem, count=1, *, strict):
        self._remove_update([(elem, count)], strict=strict)

    def _discard(self, elem):
        if elem in self.__impl:
            del self.__impl[elem]

    def _clear(self):
        self.__impl.clear()

    def _update(self, counts):
        self_impl = self.__impl
        for elem, count in counts:
            if not isinstance(count, int) or count < 0:
                raise TypeError("counts must be nonnegative integers")
            if count == 0:
                continue
            self_impl[elem] = count

    def _union_update(self, counts):
        self_impl = self.__impl
        self_impl_get = self_impl.get
        for elem, count_2 in counts:
            count_1 = self_impl_get(elem, 0)
            if count_2 > count_1:
                self_impl[elem] = count_2

    def _sum_update(self, counts):
        self_impl = self.__impl
        self_impl_get = self_impl.get
        for elem, count in counts:
            self_impl[elem] = self_impl_get(elem, 0) + count

    def _remove_update(self, counts, *, strict=False):
        self_impl = self.__impl
        self_impl_get = self_impl.get
        for elem, count in counts:
            new_count = self_impl_get(elem, 0) - count
            if new_count > 0:
                self_impl[elem] = new_count
            elif new_count == 0:
                del self_impl[elem]
            else:
                if strict:
                    raise KeyError

    def _alter_update(self, counts):
        self_impl = self.__impl
        self_impl_get = self_impl.get
        for elem, count in counts:
            cur_count = self_impl_get(elem)
            if cur_count is None:
                assert count > 0, "_alter_update expects sound changeset"
                self_impl[elem] = count
            else:
                new_count = count + cur_count
                assert new_count >= 0, "_alter_update expects sound changeset"
                if new_count > 0:
                    self_impl[elem] = new_count
                else:
                    del self_impl[elem]

    # operator methods

    def __or__(self, other):
        if not isinstance(other, _MultisetBase):
            return NotImplemented

        result = self.copy()
        result._union_update(other.multiplicities())
        return result

    def __add__(self, other):
        if not isinstance(other, _MultisetBase):
            return NotImplemented

        result = self.copy()
        result._sum_update(other.multiplicities())
        return result

    def __and__(self, other):
        if not isinstance(other, _MultisetBase):
            return NotImplemented

        result = self.copy()
        result._intersection_update(other.multiplicities())
        return result

    def __xor__(self, other):
        if not isinstance(other, _MultisetBase):
            return NotImplemented

        return self.symmetric_difference(other)

    def __mul__(self, scalar):
        if not isinstance(scalar, int):
            return NotImplemented

        return self.__class__.fromcounts((elem, count*scalar) for elem, count in self.multiplicities())

    def __le__(self, other):
        if not isinstance(other, _MultisetBase):
            return NotImplemented

        self_count = self.count
        return all(self_count(elem) <= count for elem, count in other.multiplicities())

    def __eq__(self, other):
        if not isinstance(other, _MultisetBase):
            return NotImplemented

        return self.__impl == other.__impl

    # misc amenity methods

    def __bool__(self):
        return bool(self.__impl)

    def __reversed__(self):
        yield from chain.from_iterable(starmap(repeat, reversed(self.__impl.items())))


class Bag(_MultisetBase, MutableSet):
    """Bag is a finite, unordered container with multiplicitous elements.
    """

    def extend(self, collection):
        self._extend(collection)

    def add(self, elem, *, _count=1):
        self._add(elem, _count)

    def remove(self, elem, *, _count=1):
        self._remove(elem, _count, strict=True)

    def discard(self, elem):
        self._discard(elem)

    def pop(self):
        try:
            elem = next(reversed(self.support()))
        except StopIteration:
            raise KeyError from None
        self.remove(elem)
        return elem

    def discard(self, elem):
        self._discard(elem)

    def __iadd__(self, other):
        if not isinstance(other, _MultisetBase):
            return NotImplemented

        self._extend(other)
        return self

    def __isub__(self, other):
        if not isinstance(other, _MultisetBase):
            return NotImplemented

        self._remove_update(other.multiplicities())
        return self

    def __ixor__(self, other):
        if not isinstance(other, _MultisetBase):
            return NotImplemented

    changeset = [(elem, diff) for elem, count in other.multiplicities() if ]
    self._alter_update(changeset)
    return self

class FrozenBag(_MultisetBase, Set):
    """FrozenBag is a finite, unordered, immutable container with multiplicitous elements.
    """
    __slots__ = ('__hash',)

    def __hash__(self):
        try:
            result = self.__hash
        except AttributeError:
            result = self.__hash = Set._hash(self.multiplicities())
        return result


class _BagSupportSetView(KeysView):
    __slots__ = ()
    # https://github.com/python/cpython/blob/v3.13.2/Objects/dictobject.c#L4452
    # https://github.com/python/cpython/blob/v3.13.2/Lib/_collections_abc.py#L862
    def __reverse__(self):
        yield from reversed(self._mapping)

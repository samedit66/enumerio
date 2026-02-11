import collections
import dataclasses
import functools
import itertools
import math
import operator
import random
from typing import Any, Callable, Iterable, Self

from kungfu import Error, Ok, Result

type Transform1[T, G] = Callable[[T], G]

type Predicate[T] = Transform1[T, bool]


def identity(x: Any) -> Any:
    """Return the given argument back."""
    return x


@dataclasses.dataclass(slots=True, init=False)
class Enum[T](collections.UserList):
    """A lightweight, list-like collection with convenient functional helpers inspired
    by the `Enum` module from the Elixir programming language.

    Wraps an iterable of `T` and provides methods for mapping, filtering,
    slicing and other common enumeration operations.
    """

    data: list[T]
    """Underlying list which contains the elements."""

    def __init__(self, *data: Iterable[T]) -> None:
        if len(data) == 1 and isinstance(data[0], Iterable):
            self.data = list(data[0])
        else:
            self.data = list(data)

    def __eq__(self, other: object) -> bool:
        return self.data == other

    def size(self) -> int:
        """Return the number of elements in the `Enum`.

        >>> Enum(1, 2, 3).size()
        3
        >>> Enum().size()
        0
        """
        return len(self.data)

    def has(self, element: Any) -> bool:
        """Return `True` if element is present in the `Enum`, `False` otherwise.

        >>> Enum(1, 2, 3).has(10)
        False
        >>> Enum(range(10)).has(5)
        True
        """
        return element in self

    def all(self, predicate: Predicate[T] | None = None) -> bool:
        """Return `True` if all elements satisfy predicate or are truthy if no predicate,
        `False` otherwise.

        >>> Enum(range(1, 10, 2)).all(lambda x: x % 2 == 0)
        False
        >>> Enum(range(2, 10, 2)).all(lambda x: x % 2 == 0)
        True
        >>> Enum(True, False, True).all()
        False
        """
        if predicate:
            return all(self.map(predicate))
        return all(self.data)

    def any(self, predicate: Predicate[T] | None = None) -> bool:
        """Return `True` if any element satisfies predicate or is truthy if no predicate.
        `False` otherwise.

        >>> Enum(range(1, 10, 2)).any(lambda x: x % 2 != 0)
        True
        >>> Enum(range(2, 10, 2)).any(lambda x: x % 2 != 0)
        False
        >>> Enum(True, False, True).any()
        True
        """
        if predicate:
            return any(self.map(predicate))
        return any(self.data)

    def at(self, index: int, default: T | None = None) -> T | None:
        """Return element at `index` or `default` if `index` is out of range.

        >>> Enum(1, 2, 3).at(2)
        3
        >>> Enum(1, 2, 3).at(10) is None
        True
        >>> Enum(1, 2, 3).at(10, default=42)
        42
        """
        try:
            return self[index]
        except IndexError:
            return default

    def chunked(
        self, count: int, step: int | None = None, discard: bool = False
    ) -> Enum[Enum[T]]:
        """Split the `Enum` into chunks of size `count`, advancing by `step` (defaults to `count`).
        When `discard` is `True`, does not include the last chunk with less than `count` elements.

        >>> Enum(range(10)).chunked(3)
        Enum(data=[Enum(data=[0, 1, 2]), Enum(data=[3, 4, 5]), Enum(data=[6, 7, 8]), Enum(data=[9])])
        >>> Enum(range(10)).chunked(3, discard=True)
        Enum(data=[Enum(data=[0, 1, 2]), Enum(data=[3, 4, 5]), Enum(data=[6, 7, 8])])
        >>> Enum(range(10)).chunked(4, step=3)
        Enum(data=[Enum(data=[0, 1, 2, 3]), Enum(data=[3, 4, 5, 6]), Enum(data=[6, 7, 8, 9])])
        """
        chunked = []

        step = step or count
        for i in range(0, len(self), step):
            chunk = self[i : i + count]

            if discard and len(chunk) < count:
                break

            chunked.append(Enum(chunk))

            if i + count >= len(self):
                break

        return Enum(chunked)

    def concat[G](self) -> Enum[G]:
        """Given an `Enum` of iterables, concatenates them into a single `Enum`.

        >>> Enum([1, 2, 3], [4, 5, 6]).concat()
        Enum(data=[1, 2, 3, 4, 5, 6])
        """
        return Enum(itertools.chain.from_iterable(self))

    def drop(self, amount: int) -> Enum[T]:
        """Return a new `Enum` with `amount` elements removed from the head (negative drops from tail).

        >>> Enum(1, 2, 3).drop(2)
        Enum(data=[3])
        >>> Enum(1, 2, 3).drop(-2)
        Enum(data=[1])
        >>> Enum(1, 2, 3).drop(0)
        Enum(data=[1, 2, 3])
        """
        if amount < 0:
            return self[:amount]
        return self[amount:]

    def drop_every(self, nth: int) -> Enum[T]:
        """Returns a list of every nth element in the `Enum` dropped, starting with the first element.
        The first element is always dropped, unless `nth` is `0`.

        >>> Enum(1, 2, 3, 4, 5).drop_every(2)
        Enum(data=[2, 4])
        >>> Enum(1, 2, 3, 4, 5).drop_every(0)
        Enum(data=[1, 2, 3, 4, 5])
        """
        if nth == 0:
            return self
        result = []
        for i in range(len(self)):
            if i % nth != 0:
                result.append(self[i])
        return Enum(result)

    def drop_while(self, predicate: Predicate[T]) -> Enum[T]:
        """Remove leading elements while `predicate` is True.

        >>> Enum(1, 2, 3, 1).drop_while(lambda x: x < 3)
        Enum(data=[3, 1])
        >>> Enum(1, 1, 1).drop_while(lambda x: x == 1)
        Enum(data=[])
        """
        return Enum(itertools.dropwhile(predicate, self))

    def each[G](self, procedure: Transform1[T, G]) -> None:
        """Call `procedure` for every element (side effects only).

        >>> out = []
        >>> Enum(1, 2, 3).each(lambda x: out.append(x * 2))
        >>> out
        [2, 4, 6]
        """
        for element in self:
            procedure(element)

    def empty(self) -> bool:
        """Return `True` if the `Enum` has no elements.

        >>> Enum().empty()
        True
        >>> Enum(1).empty()
        False
        """
        return len(self) == 0

    def fetch(self, index: int) -> Result[T, str]:
        """Return `Ok(value)` at `index` or `Error` if out of range.

        >>> Enum(10, 20).fetch(1)
        <Result: Ok(20)>
        >>> Enum(10, 20).fetch(5)
        <Result: Error('fetch(): invalid index: 5')>
        """
        try:
            return Ok(self[index])
        except IndexError:
            return Error(f"fetch(): invalid index: {index}")

    def map[G](self, transform: Transform1[T, G]) -> Enum[G]:
        """Transform each element and return a new `Enum`.

        >>> Enum(1, 2, 3).map(lambda x: x * 2)
        Enum(data=[2, 4, 6])
        """
        return Enum(map(transform, self))

    def map_join(self, transform: Transform1[T, str], joiner: str = "") -> str:
        """Map elements to strings and join them.

        >>> Enum(1, 2, 3).map_join(str, ",")
        '1,2,3'
        """
        return joiner.join(self.map(transform))

    def min(self) -> T:
        """Return the smallest element.

        >>> Enum(3, 1, 2).min()
        1
        """
        if self.empty():
            raise ValueError("min(): enum is empty")
        return min(self)

    def min_by(self, key: Transform1[T, Any]) -> T:
        """Return the element with the smallest key value.

        >>> Enum("aaa", "b", "cc").min_by(len)
        'b'
        """
        if self.empty():
            raise ValueError("min(): enum is empty")
        return min(self, key=key)

    def max(self) -> T:
        """Return the largest element.

        >>> Enum(3, 1, 2).max()
        3
        """
        if self.empty():
            raise ValueError("max(): enum is empty")
        return max(self)

    def max_by(self, key: Transform1[T, Any]) -> T:
        """Return the element with the largest key value.

        >>> Enum("aaa", "b", "cc").max_by(len)
        'aaa'
        """
        if self.empty():
            raise ValueError("max(): enum is empty")
        return max(self, key=key)

    def min_max(self) -> tuple[T, T]:
        """Return (minimum, maximum).

        >>> Enum(3, 1, 5, 2).min_max()
        (1, 5)
        """
        if self.empty():
            raise ValueError("min_max(): enum is empty")
        return (self.min(), self.max())

    def min_max_by(self, key: Transform1[T, Any]) -> tuple[T, T]:
        """Return (min_by, max_by) using key function.

        >>> Enum("a", "bbb", "cc").min_max_by(len)
        ('a', 'bbb')
        """
        if self.empty():
            raise ValueError("min_max(): enum is empty")
        return (self.min_by(key), self.max_by(key))

    def prod(self) -> int:
        """Return the product of elements.

        >>> Enum(2, 3, 4).prod()
        24
        """
        return math.prod(self)

    def prod_by(self, mapper: Transform1[T, int]) -> int:
        """Map elements and multiply the results.

        >>> Enum(1, 2, 3).prod_by(lambda x: x + 1)
        24
        """
        return math.prod(self.map(mapper))

    def filter(self, predicate: Predicate[T]) -> Enum[T]:
        """Keep elements where predicate is `True`.

        >>> Enum(1, 2, 3, 4).filter(lambda x: x % 2 == 0)
        Enum(data=[2, 4])
        """
        return Enum(filter(predicate, self))

    def filter_map[G, E](self, transform: Transform1[T, Result[G, E]]) -> Enum[G]:
        """Keep only `Ok` values returned by `transform`.

        >>> Enum(1, 2, 3).filter_map(lambda x: Ok(x*2) if x>1 else Error("bad"))
        Enum(data=[4, 6])
        """
        result = []
        for element in self:
            match transform(element):
                case Ok(x):
                    result.append(x)
                case Error(_e):
                    pass
        return Enum(result)

    def flatten(self) -> Enum:
        """Recursively flatten nested iterables.

        >>> Enum([1, [2, 3], [[4]]]).flatten()
        Enum(data=[1, 2, 3, 4])
        """
        result = []
        for element in self:
            if isinstance(element, Iterable):
                result.extend(Enum(element).flatten())
            else:
                result.append(element)
        return Enum(result)

    def flat_map[G](self, transform: Transform1[T, Iterable[G]]) -> Enum[G]:
        """Transform each element into an `Iterable` and concat them after.

        >>> Enum([1, 3], [4, 6]).flat_map(lambda l: range(l[0], l[1]+1))
        Enum(data=[1, 2, 3, 4, 5, 6])
        """
        return self.map(transform).concat()

    def find(self, predicate: Predicate[T], default: T | None = None) -> T | None:
        """Return first matching element or `default`.

        >>> Enum(1, 3, 4).find(lambda x: x % 2 == 0)
        4
        >>> Enum(1, 3).find(lambda x: x % 2 == 0, 0)
        0
        """
        for element in self:
            if predicate(element):
                return element
        return default

    def find_index(self, predicate: Predicate[T]) -> int | None:
        """Return index of first matching element.

        >>> Enum(5, 8, 9).find_index(lambda x: x % 2 == 0)
        1
        """
        for i, element in enumerate(self):
            if predicate(element):
                return i
        return None

    def find_value[G](
        self, transform: Transform1[T, G], default: G | None = None
    ) -> G | None:
        """Return first truthy transformed value.

        >>> Enum(1, 2, 3).find_value(lambda x: x if x > 2 else None)
        3
        """
        for element in self:
            if r := transform(element):
                return r
        return default

    def freq(self) -> Map[T, int]:
        """Count occurrences of each element.

        >>> Enum(1, 1, 2, 3, 3, 3).freq()
        Map(data={1: 2, 2: 1, 3: 3})
        """
        return self.freq_by(identity)

    def freq_by[G](self, key_fun: Transform1[T, G]) -> Map[G, int]:
        """Count occurrences of each element transformed by `key_fun`.

        >>> Enum("a", "A", "b", "B").freq_by(str.upper)
        Map(data={'A': 2, 'B': 2})
        """
        result = collections.defaultdict(int)
        for element in self:
            result[key_fun(element)] += 1
        return Map(result)

    def group_by[G, E](
        self,
        key_fun: Transform1[T, G] = identity,
        value_fun: Transform1[T, E] = identity,
    ) -> Map[G, Enum[E]]:
        """Group elements by key function.

        >>> Enum(1, 2, 3, 4).group_by(lambda x: x % 2)
        Map(data={1: Enum(data=[1, 3]), 0: Enum(data=[2, 4])})
        """
        groups = collections.defaultdict(Enum)
        for element in self:
            groups[key_fun(element)].append(value_fun(element))
        return Map(groups)

    def join(self, joiner: str = "") -> str:
        """Join string elements.

        >>> Enum("a","b","c").join("-")
        'a-b-c'
        """
        return joiner.join(self)

    def reject(self, predicate: Predicate[T]) -> Enum[T]:
        """Remove elements where predicate is `True`.

        >>> Enum(1, 2, 3, 4).reject(lambda x: x % 2 == 0)
        Enum(data=[1, 3])
        """
        return self.filter(lambda x: not predicate(x))

    def rev(self) -> Enum[T]:
        """Return reversed `Enum`.

        >>> Enum(1, 2, 3).rev()
        Enum(data=[3, 2, 1])
        """
        return Enum(reversed(self))

    def random(self) -> T:
        """Return a random element.

        >>> Enum(1).random()
        1
        """
        if self.empty():
            raise ValueError("random(): Enum is empty")
        return random.choice(self)

    def reduce[G](self, fun: Callable[[G, T], G], acc: G) -> G:
        """Reduce elements into a single value.

        >>> Enum(1, 2, 3).reduce(lambda acc, x: acc + x, 0)
        6
        """
        return functools.reduce(fun, self, initial=acc)

    def shuffle(self) -> Enum[T]:
        """Return a shuffled Enum.

        >>> len(Enum(1,2,3).shuffle())
        3
        """
        copied = self.copy()
        random.shuffle(copied)
        return Enum(copied)

    def sorted(self) -> Enum[T]:
        """Return a sorted Enum.

        >>> Enum(3,1,2).sorted()
        Enum(data=[1, 2, 3])
        """
        return Enum(sorted(self))

    def split(self, count: int) -> tuple[Enum[T], Enum[T]]:
        """Split into first N and remainder.

        >>> Enum(1, 2, 3, 4).split(2)
        (Enum(data=[1, 2]), Enum(data=[3, 4]))
        """
        return (self[:count], self[count:])

    def split_while(self, predicate: Predicate[T]) -> tuple[Enum[T], Enum[T]]:
        """Split while `predicate` holds.

        >>> Enum(1, 2, 3, 1).split_while(lambda x: x < 3)
        (Enum(data=[1, 2]), Enum(data=[3, 1]))
        """
        truthy = []
        falsy = []
        for i, element in enumerate(self):
            if predicate(element):
                truthy.append(element)
            else:
                falsy.extend(self[i:])
                break
        return (Enum(truthy), Enum(falsy))

    def split_with(self, predicate: Predicate[T]) -> tuple[Enum[T], Enum[T]]:
        """Partition by `predicate`.

        >>> Enum(1, 2, 3, 4).split_with(lambda x: x % 2 == 0)
        (Enum(data=[2, 4]), Enum(data=[1, 3]))
        """
        truthy = []
        falsy = []
        for element in self:
            if predicate(element):
                truthy.append(element)
            else:
                falsy.append(element)
        return (Enum(truthy), Enum(falsy))

    def sum(self) -> int:
        """Return sum of elements.

        >>> Enum(1,2,3).sum()
        6
        """
        return sum(self)

    def sum_by(self, mapper: Transform1[T, int]) -> int:
        """Map then sum.

        >>> Enum(1, 2, 3).sum_by(lambda x: x * 2)
        12
        """
        return sum(self.map(mapper))

    def take(self, amount: int) -> Enum[T]:
        """Take first `amount` elements.

        >>> Enum(1, 2, 3, 4).take(2)
        Enum(data=[1, 2])
        """
        if amount < 0:
            return Enum(self[amount:])
        return Enum(self[:amount])

    def take_every(self, nth: int) -> Enum[T]:
        """Take every `nth` element.

        >>> Enum(1, 2, 3, 4, 5).take_every(2)
        Enum(data=[1, 3, 5])
        """
        if nth == 0:
            return Enum([])
        return Enum(self[::nth])

    def take_random(self, count: int) -> Enum[T]:
        """Return random subset.

        >>> len(Enum(1, 2, 3).take_random(2))
        2
        """
        return self.shuffle().take(count)

    def take_while(self, predicate: Predicate[T]) -> Enum[T]:
        """Take elements while `predicate` holds.

        >>> Enum(1, 2, 3, 1).take_while(lambda x: x < 3)
        Enum(data=[1, 2])
        """
        return Enum(itertools.takewhile(predicate, self))

    def uniq(self) -> Enum[T]:
        """Remove duplicates preserving order.

        >>> Enum(1, 1, 2, 2, 3).uniq()
        Enum(data=[1, 2, 3])
        """
        return self.uniq_by(identity)

    def uniq_by[G](self, key_fun: Transform1[T, G]) -> Enum[G]:
        """Remove duplicates based on `key_fun` preserving order.

        >>> Enum("aaa", "bbb", "cc", "dd").uniq_by(len)
        Enum(data=['aaa', 'cc'])
        """
        result = []
        keys = []
        for key, element in zip(self.map(key_fun), self):
            if key not in keys:
                keys.append(key)
                result.append(element)
        return Enum(result)

    def zip(self) -> Enum[tuple]:
        """Zip inner iterables together.

        >>> Enum([1, 2], [3, 4]).zip()
        Enum(data=[(1, 3), (2, 4)])
        """
        return Enum(zip(*self))

    def zip_with(self, zipper) -> Enum[tuple]:
        """Zip and transform elements.

        >>> Enum([1, 2],[3, 4]).zip_with(lambda a, b: a + b)
        Enum(data=[4, 6])
        """
        return self.zip().map(lambda t: zipper(*t))

    def pluck(self, *keys: Any) -> Enum[Any]:
        """Select key values from each element.

        >>> Enum([1, 2, 3], [4, 5, 6]).pluck(0)
        Enum(data=[1, 4])
        >>> Enum([1, 2, 3], [4, 5, 6]).pluck(2, 0)
        Enum(data=[(3, 1), (6, 4)])
        >>> Enum({"a": 1}, {"a": 2}).pluck("a")
        Enum(data=[1, 2])
        """
        return self.map(operator.itemgetter(*keys))

    def into(self, convert, mapper=None):
        """Convert `Enum` into another container.

        >>> Enum(1,2,3).into(list)
        [1, 2, 3]
        """
        if mapper is None:
            return convert(self)
        return convert(self.map(mapper))

    def with_index(self, start: int = 0) -> Enum[tuple[int, T]]:
        """Transform each element into a 2-element tuple (index, element).

        >>> Enum("abc").with_index()
        Enum(data=[(0, 'a'), (1, 'b'), (2, 'c')])
        >>> Enum("abc").with_index(start=1)
        Enum(data=[(1, 'a'), (2, 'b'), (3, 'c')])
        """
        return Enum(enumerate(self, start=start))

    def tap(self, interceptor: Callable[[Enum[T]], Any]) -> Self:
        """Taps into a method chain, in order to perform some operation,
        returns the same object without changing it.

        >>> Enum(1, 2, 3).tap(print).sum()
        Enum(data=[1, 2, 3])
        6
        """
        interceptor(self)
        return self

    def starmap(self, transform):
        """Treat each `Enum` element as arguments to unpack and then pass to `transform`.

        >>> Enum([1, 2], [3, 4], [5, 6]).starmap(lambda a, b: a + b)
        Enum(data=[3, 7, 11])
        """
        return Enum(itertools.starmap(transform, self))


@dataclasses.dataclass(slots=True, init=False)
class Map[K, V](collections.UserDict):
    """A lightweight, dict-like collection with functional helpers inspired
    by the `Enum` and `Map` modules from the Elixir programming language.

    Wraps a mapping of keys `K` to values `V` and provides convenient methods
    for transformation, filtering, and conversion, often returning `Enum`
    or `Map` to enable fluent pipelines.
    """

    data: dict[K, V]
    """Underlying dictionary which stores key–value pairs."""

    def __init__(self, pairs_or_mapping: Iterable[tuple[K, V]] | dict) -> None:
        """Create a new `Map` from key–value pairs or an existing mapping."""
        self.data = dict(pairs_or_mapping)

    def __eq__(self, other: object, /) -> bool:
        """Return `True` if the underlying mapping is equal to `other`."""
        return self.data == other

    def delete(self, key: K) -> Map[K, V]:
        """Remove a `key`.

        >>> Map({"a": 1,"b": 2}).delete("a")
        Map(data={'b': 2})
        """
        return self.reject(lambda k, _v: k == key)

    def drop(self, *keys: K) -> Map[K, V]:
        """Remove multiple `keys`.

        >>> Map({"a": 1,"b": 2,"c": 3}).drop("a", "c")
        Map(data={'b': 2})
        """
        return self.reject(lambda k, _v: k in keys)

    def has_key(self, key: K) -> bool:
        """Check if `key` exists.

        >>> Map({"a": 1}).has_key("a")
        True
        >>> Map({"a": 1}).has_key("b")
        False
        """
        return key in self

    def map[G](self, transform: Callable[[K, V], G]) -> Enum[G]:
        """Transform each key-value pair.

        >>> Map({"a": 1,"b": 2}).map(lambda k, v: v * 2)
        Enum(data=[2, 4])
        """
        return self.pairs().map(lambda pair: transform(pair[0], pair[1]))

    def filter(self, predicate: Callable[[K, V], bool]) -> Map[K, V]:
        """Keep pairs matching `predicate`.

        >>> Map({"a": 1,"b": 2}).filter(lambda k, v: v > 1)
        Map(data={'b': 2})
        """
        return self.pairs().filter(lambda pair: predicate(pair[0], pair[1])).into(Map)

    def reject(self, predicate: Callable[[K, V], bool]) -> Map[K, V]:
        """Remove pairs matching `predicate`.

        >>> Map({"a": 1, "b": 2}).reject(lambda k, v: v > 1)
        Map(data={'a': 1})
        """
        return self.filter(lambda k, v: not predicate(k, v))

    def to_keys(self) -> Enum[K]:
        """Return all keys.

        >>> Map({"a": 1,"b": 2}).to_keys().sorted()
        Enum(data=['a', 'b'])
        """
        return Enum(super().keys())

    def to_values(self) -> Enum[V]:
        """Return all values.

        >>> Map({"a": 1,"b": 2}).to_values().sorted()
        Enum(data=[1, 2])
        """
        return Enum(super().values())

    def pairs(self) -> Enum[tuple[K, V]]:
        """Return key-value pairs.

        >>> Map({"a": 1}).pairs()
        Enum(data=[('a', 1)])
        """
        return Enum(self.items())

    def take(self, *keys: K) -> Map[K, V]:
        """Keep only selected `keys`.

        >>> Map({"a": 1, "b": 2}).take("b")
        Map(data={'b': 2})
        """
        result = {}
        for key in keys:
            if key not in self.keys():
                continue
            result[key] = self[key]
        return Map(result)

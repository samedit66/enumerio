import collections
import copy
import dataclasses
import functools
import itertools
import math
import random
from typing import Any, Callable, Iterable

from kungfu import Error, Ok, Result

type Transform1[T, G] = Callable[[T], G]

type Predicate[T] = Transform1[T, bool]

type Number = int | float  # TODO: maybe use `numbers` package instead


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
        """Return the number of elements in the `Enum`."""
        return len(self.data)

    def member(self, element: Any) -> bool:
        """Return `True` if element is present in the `Enum`."""
        return element in self

    def all(self, predicate: Predicate[T] | None = None) -> bool:
        """Return True if all elements satisfy predicate or are truthy if no predicate."""
        if predicate:
            return all(self.map(predicate))
        return all(self.data)

    def any(self, predicate: Predicate[T] | None = None) -> bool:
        """Return True if any element satisfies predicate or is truthy if no predicate."""
        if predicate:
            return any(self.map(predicate))
        return any(self.data)

    def at(self, index: int, default: T | None = None) -> T | None:
        """Return element at index or default if index is out of range."""
        try:
            return self[index]
        except IndexError:
            return default

    def chunked(
        self, count: int, step: int | None = None, discard: bool = False
    ) -> Enum[Enum[T]]:
        """Split the `Enum` into chunks of size `count`, advancing by `step` (defaults to `count`).
        When `discard` is `True`, does not include the last chunk with less than `count` elements.
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

    def concat(self) -> Enum[Any]:
        """Given an `Enum` of iterables, concatenates them into a single `Enum`."""
        result = []
        for element in self:
            result.extend(element)
        return Enum(result)

    def drop(self, amount: int) -> Enum[T]:
        """Return a new `Enum` with `amount` elements removed from the head (negative drops from tail)."""
        match amount:
            case 0:
                return self
            case _ if amount > 0:
                return Enum(self[amount:])
            case _:  # amount < 0
                return Enum(self[:amount])

    def drop_every(self, nth: int) -> Enum[T]:
        """Returns a list of every nth element in the `Enum` dropped, starting with the first element.
        The first element is always dropped, unless `nth` is `0`.
        """
        if nth == 0:
            return self
        result = []
        for i in range(len(self)):
            if i % nth != 0:
                result.append(self[i])
        return Enum(result)

    def drop_while(self, predicate: Predicate[T]) -> Enum[T]:
        """Drops elements at the beginning of the `Enum` while `predicate` returns a truthy value."""
        for i, element in enumerate(self):
            if not predicate(element):
                return self[i:]
        return Enum()

    def each[G](self, procedure: Transform1[T, G]) -> None:
        """Invokes the given `procedure` for each element.
        Used only for producing side effects. Otherwise, use `map`.
        """
        for element in self:
            procedure(element)

    def empty(self) -> bool:
        """Return `True` if `Enum` contains no elements."""
        return len(self) == 0

    def fetch(self, index: int) -> Result[T, str]:
        """Attempt to return the element at index wrapped in `Ok`, or `Error` if out of range."""
        try:
            return Ok(self[index])
        except IndexError:
            return Error(f"fetch(): invalid index: {index}")

    def map[G](self, transform: Transform1[T, G]) -> Enum[G]:
        """Return a new `Enum` of `transform(x)` for each element x."""
        return Enum([transform(x) for x in self])

    def map_join(self, transform: Transform1[T, str], joiner: str = "") -> str:
        """Map each element to a string and join them with `joiner`."""
        return joiner.join(self.map(transform))

    def min(self) -> T:
        """Return the minimum. Raise `ValueError` when `Enum `is empty."""
        if self.empty():
            raise ValueError("min(): enum is empty")
        return min(self)

    def min_by(self, key: Transform1[T, Any]) -> T:
        """Return the minimum as calculated by `key`. Raise `ValueError` when `Enum` is empty."""
        if self.empty():
            raise ValueError("min(): enum is empty")
        return min(self, key=key)

    def max(self) -> T:
        """Return the maximum. Raise `ValueError` when `Enum` is empty."""
        if self.empty():
            raise ValueError("max(): enum is empty")
        return max(self)

    def max_by(self, key: Transform1[T, Any]) -> T:
        """Return the maximum as calculated by key. Raise `ValueError` when `Enum` is empty."""
        if self.empty():
            raise ValueError("max(): enum is empty")
        return max(self, key=key)

    def min_max(self) -> tuple[T, T]:
        """Return both minimum and maximum of the elements. Raise ValueError when Enum is empty."""
        if self.empty():
            raise ValueError("min_max(): enum is empty")
        return (self.min(), self.max())

    def min_max_by(self, key: Transform1[T, Any]) -> tuple[T, T]:
        """Return both minimum and maximum of `Enum` as calculated by `key`.
        Raise `ValueError` when `Enum` is empty.
        """
        if self.empty():
            raise ValueError("min_max(): enum is empty")
        return (self.min_by(key), self.max_by(key))

    def prod(self) -> Number:
        """Return the product of elements."""
        return math.prod(self)

    def prod_by(self, mapper: Transform1[T, Number]) -> Number:
        """Return the product of elements, mapping each element first."""
        return math.prod(self.map(mapper))

    def filter(self, predicate: Predicate[T]) -> Enum[T]:
        """Return a new `Enum` containing only elements for which `predicate(element)` is True."""
        return Enum([x for x in self if predicate(x)])

    def filter_map[G, E](self, transform: Transform1[T, Result[G, E]]) -> Enum[G]:
        """Return a new `Enum` containing only the elements from the first list for which the given function returns `Ok(_)`."""
        result = []
        for element in self:
            match transform(element):
                case Ok(x):
                    result.append(x)
                case Error(_e):
                    pass
        return Enum(result)

    def flatten(self) -> Enum:
        """Return a new `Enum` which contains no inner `Enum`'s."""
        result = []
        for element in self:
            if isinstance(element, Iterable):
                result.extend(Enum(element).flatten())
            else:
                result.append(element)
        return Enum(result)

    def find(self, predicate: Predicate[T], default: T | None = None) -> T | None:
        """Return the first element matching predicate or `default` if none match."""
        for element in self:
            if predicate(element):
                return element
        return default

    def find_index(self, predicate: Predicate[T]) -> int | None:
        """Return the index of the first element matching `predicate` or `None` if not found."""
        for i, element in enumerate(self):
            if predicate(element):
                return i
        return None

    def find_value[G](
        self, transform: Transform1[T, G], default: G | None = None
    ) -> G | None:
        """Return the first truthy result of `transform` or `default` if none."""
        for element in self:
            if r := transform(element):
                return r
        return default

    def frequencies(self) -> Map[T, int]:
        """Return a dict mapping each distinct element to its occurrence count."""
        result = collections.defaultdict(int)
        for element in self:
            result[element] += 1
        return Map(result)

    def group_by[G, E](
        self, key_fun: Transform1[T, G], value_fun: Transform1[T, E] | None = None
    ) -> dict[G, Enum[E]]:
        """Splits the `Enum` into groups based on `key_fun`.
        The result is a `dict` where each key is given by `key_fun` and each value is a list of elements given by `value_fun`.
        """
        groups = collections.defaultdict(Enum)
        for element in self:
            if value_fun is None:
                groups[key_fun(element)].append(element)
            else:
                groups[key_fun(element)].append(value_fun(element))
        return groups

    def join(self, joiner: str = "") -> str:
        """Concatenate elements (assumed strings) using `joiner` and return the result."""
        return joiner.join(self)

    def reject(self, predicate: Predicate[T]) -> Enum[T]:
        """Return a new `Enum` excluding elements for which `predicate` is `True`."""
        return self.filter(lambda x: not predicate(x))

    def reversed(self, tail: Iterable[T] | None = None):
        """Return a new `Enum` with elements in reverse order, optionally appending `tail`."""
        if tail:
            return Enum(list(reversed(self)) + list(tail))
        return Enum(list(reversed(self)))

    def random(self) -> T:
        """Return a randomly selected element. Raises `ValueError` when `Enum` is empty."""
        if self.empty():
            raise ValueError("random(): Enum is empty")
        return random.choice(self)

    def reduce[G](self, fun: Callable[[G, T], G], acc: G) -> G:
        """Reduces `Enum` to a single value with the given `fun` and the initial `acc` value."""
        return functools.reduce(fun, self, initial=acc)

    def shuffle(self) -> Enum[T]:
        """Return a new `Enum` with elements randomly shuffled."""
        copy = self.copy()
        random.shuffle(copy)
        return Enum(copy)

    def sorted(self) -> Enum[T]:
        """Return a new `Enum` with elements sorted in ascending order."""
        return Enum(sorted(self))

    def split(self, count: int) -> tuple[Enum[T], Enum[T]]:
        """Split into a pair of `Enum`s: first `count` elements and the rest."""
        first, second = self[:count], self[count:]
        return (Enum(first), Enum(second))

    def split_while(self, predicate: Predicate[T]) -> tuple[Enum[T], Enum[T]]:
        """Split into (leading elements matching `predicate`, remaining elements)."""
        truthy = []
        falsy = []
        for i, element in enumerate(self):
            if predicate(element):
                truthy.append(element)
            else:
                falsy.extend(self[i:])
        return (Enum(truthy), Enum(falsy))

    def split_with(self, predicate: Predicate[T]) -> tuple[Enum[T], Enum[T]]:
        """Partition elements into a pair (matching `predicate,` not matching `predicate`)."""
        truthy = []
        falsy = []
        for element in self:
            if predicate(element):
                truthy.append(element)
            else:
                falsy.append(element)
        return (Enum(truthy), Enum(falsy))

    def sum(self) -> Number:
        """Return the sum of elements."""
        return sum(self)

    def sum_by(self, mapper: Transform1[T, Number]) -> Number:
        """Return the sum of elements mapping each element first."""
        return sum(self.map(mapper))

    def take(self, amount: int) -> Enum[T]:
        """Return a new `Enum` with the first `amount` elements (negative takes from tail)."""
        match amount:
            case 0:
                return Enum([])
            case _ if amount > 0:
                return Enum(self[:amount])
            case _:  # amount < 0
                return Enum(self[amount:])

    def take_every(self, nth: int) -> Enum[T]:
        """Return every `nth` element as a new `Enum`; nth==0 returns an empty `Enum`."""
        if nth == 0:
            return Enum([])
        return Enum(self[::nth])

    def take_random(self, count: int) -> Enum[T]:
        """Return `count` randomly selected elements (without replacement) as a new `Enum`."""
        return self.shuffle().take(count)

    def take_while(self, predicate: Predicate[T]) -> Enum[T]:
        """Return elements from the start which satisfy the `predicate`."""
        taken = list(itertools.takewhile(predicate, self))
        return Enum(taken)

    def uniq(self) -> Enum[T]:
        """Return a new `Enum`, removing all duplicate elements.
        The first occurence of each element is kept and the overall order is preserved.
        """
        result = []
        for element in self:
            if element not in result:
                result.append(element)
        return Enum(result)

    def zip(self) -> Enum[Any]:
        """Zips corresponding elements from a finite collection of enumerables into a list of tuples.
        The zipping finishes as soon as any enumerable in the given collection completes.
        """
        zipped = list(zip(self))
        return Enum(zipped)

    def sublist(self, *indices: Any) -> Enum[Any]:
        """Extract elements at the given indices from each sub-sequence.
        Assumes each element of the `Enum` is indexable. Returns a new `Enum`
        where each element is an `Enum` containing values from the specified indices.
        """
        result = []
        for inner in self:
            sublist = list(inner[i] for i in indices)
            result.append(Enum(sublist))
        return Enum(result)

    def subdict(self, *keys: Any) -> Enum[Any]:
        """Extract key-value pairs for the given keys from each sub-dictionary.
        Assumes each element of the `Enum` is a mapping. Returns a new `Enum`
        of dictionaries containing only the specified keys.
        """
        result = []
        for inner in self:
            result.append(
                Map((key, value) for key, value in inner.items() if key in keys)
            )
        return Enum(result)

    def select(self, *keys: Any) -> Enum[Any]:
        """Select the values for `keys` from each element.
        Assumes each element supports key-based access (e.g. `dict`, mapping or `list`).
        Returns a new `Enum` containing `element[key]` for every element.
        When only one key given, also flattens output.
        """
        result = []
        for subseq in self:
            result.append(tuple(subseq[key] for key in keys))

        if len(keys) == 1:
            return Enum(result).flatten()
        return Enum(result)

    def to_map(self) -> Map:
        """Convert `Enum` to `Map`. Assumes each element is a tuple-like pair."""
        result = {}
        for key, value in self:
            result[key] = value
        return Map(result)


@dataclasses.dataclass(slots=True, init=False)
class Map[K, V](collections.UserDict):
    data: dict[K, V]

    def __init__(self, pairs_or_mapping: Iterable[tuple[K, V]] | dict) -> None:
        self.data = dict(pairs_or_mapping)

    def __eq__(self, other: object, /) -> bool:
        return self.data == other

    def map[G](self, transform: Callable[[K, V], G]) -> Enum[G]:
        return Enum((transform(k, v) for k, v in self.items()))

    def filter(self, predicate: Callable[[K, V], bool]) -> Map[K, V]:
        return Map([(k, v) for k, v in self.items() if predicate(k, v)])

    def reject(self, predicate: Callable[[K, V], bool]) -> Map[K, V]:
        return Map([(k, v) for k, v in self.items() if not predicate(k, v)])

    def to_keys(self) -> Enum[K]:
        return Enum(super().keys())

    def to_values(self) -> Enum[V]:
        return Enum(super().values())

    def to_enum(self) -> Enum[tuple[K, V]]:
        return Enum(list(self.items()))

    def take(self, *keys: K) -> Map[K, V]:
        result = {}
        for key in keys:
            if key not in self.keys():
                continue
            result[key] = self[key]
        return Map(result)

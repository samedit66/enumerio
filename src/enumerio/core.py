import collections
import dataclasses
from collections.abc import Collection
from typing import Any, Callable

type Transform1[T, G] = Callable[[T], G]

type Predicate[T] = Transform1[T, bool]


@dataclasses.dataclass(slots=True, init=False)
class Enum[T](collections.UserList):
    data: list[T]

    def __init__(self, data: Collection[T]) -> None:
        self.data = list(data)

    def __eq__(self, other: object) -> bool:
        return self.data == other

    # Functions defined in Enumerable protocol

    def len(self) -> int:
        return len(self.data)

    def member(self, element: Any) -> bool:
        return element in self

    # Functions defined in Enum module

    def all(self, predicate: Predicate[T] | None = None) -> bool:
        if predicate:
            return all(self.map(predicate))
        return all(self.data)

    def any(self, predicate: Predicate[T] | None = None) -> bool:
        if predicate:
            return any(self.map(predicate))
        return any(self.data)

    def at(self, index: int, default: T | None = None) -> T | None:
        try:
            return self[index]
        except IndexError:
            return default

    def chunk_every(self, count: int) -> Enum[Enum[T]]:
        chunked = []

        for i in range(0, len(self), count):
            chunk = self[i : i + count]
            chunked.append(Enum(chunk))

        return Enum(chunked)

    def map[G](self, transform: Transform1[T, G]) -> Enum[G]:
        return Enum([transform(x) for x in self.data])

    def filter(self, predicate: Predicate[T]) -> Enum[T]:
        return Enum([x for x in self.data if predicate(x)])

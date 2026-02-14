import abc
import dataclasses
import functools
from typing import Any, Callable, ClassVar, Optional, cast


class Option[T](abc.ABC):
    """Abstract generic Option[T] base type."""

    def __init__(self) -> None:
        raise NotImplementedError(
            "Option: it is not allowed to create instances of `Option` class"
        )

    def is_some(self) -> bool:
        """Return `True` if this `Option` is a `Some` containing a value."""
        return isinstance(self, Some)

    def is_nothing(self) -> bool:
        """Return `True` if this `Option` represents absence of a value (`Nothing`)."""
        return isinstance(self, Nothing)

    def unwrap_or(self, default: Any) -> Any:
        """Return contained value if `Some`, otherwise return `default`."""
        match self:
            case Some(value):
                return value
            case _:
                return default

    def map(self, fn: Callable[[T], Any]) -> Option:
        """Transform the contained value using `fn` if `Some`, else return `Nothing`."""
        match self:
            case Some(value):
                return Some(fn(value))
            case _:
                return self

    def bind(self, fn: Callable[[T], Option[Any]]) -> Option:
        """Flat-map: apply `fn` returning `Option` if `Some`, else return `Nothing`."""
        match self:
            case Some(value):
                return fn(value)
            case _:
                return self

    @staticmethod
    def from_value(value: T | None) -> Option[T]:
        """Make `Option` from a `value`, return `Some` if `value` is not `None`."""
        if value is None:
            return Nothing()
        return Some(value)


@dataclasses.dataclass(frozen=True, slots=True)
class Some[T](Option[T]):
    """Represents presence of a value."""

    __match_args__ = ("value",)
    value: T


@dataclasses.dataclass(frozen=True, slots=True)
class Nothing(Option[Any]):
    """Represents absence of a value."""

    __match_args__ = ()

    # store the single instance as a class var so dataclasses doesn't treat it as a field
    _instance: ClassVar[Optional[Nothing]] = None

    def __new__(cls) -> Nothing:
        """Return the single Nothing instance (create it once)."""
        if cls._instance is None:
            # use object.__new__ to avoid calling Option.__init__
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """No-op: avoid calling Option.__init__ which raises."""
        # dataclasses would normally call __init__ on instances, but we override
        # to prevent Option.__init__ from running.
        return

    def __repr__(self) -> str:
        return "Nothing()"


def maybe[**P, T](fn: Callable[P, T]) -> Callable[P, Option[T]]:
    """
    Decorator that turns a function's return value into an `Option[T]`.

    Behavior:
    - If `fn` raises an `Exception`, return `Nothing`.
    - If `fn` returns `None`, return `Nothing`.
    - If `fn` returns an `Option` already, return it (typed as `Option[T]`).
    - Otherwise wrap the returned value in `Some(value)`.
    """

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Option[T]:
        try:
            result = fn(*args, **kwargs)
        except Exception:
            # suppress exceptions derived from Exception and return Nothing
            return Nothing()

        # preserve Option results
        if isinstance(result, Option):
            # mypy/pyright can't always infer this cast; runtime is safe
            return cast(Option[T], result)

        # None -> Nothing, otherwise wrap into Some
        if result is None:
            return Nothing()

        return Some(result)

    return wrapper

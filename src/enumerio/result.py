import abc
import dataclasses
import functools
from typing import Any, Callable, cast


class Result[T, E](abc.ABC):
    """Abstract generic Result[T, E] base type."""

    def __init__(self) -> None:
        raise NotImplementedError(
            "Result: it is not allowed to create instances of `Result` class"
        )

    def is_ok(self) -> bool:
        """Return True if this is an Ok(value)."""
        return isinstance(self, Ok)

    def is_err(self) -> bool:
        """Return True if this is an Err(error)."""
        return isinstance(self, Err)

    def unwrap_or(self, default: Any) -> Any:
        """Return value for Ok, otherwise return `default`."""
        match self:
            case Ok(value):
                return value
            case _:
                return default

    def map(self, fn: Callable[[T], Any]) -> Result[Any, E]:
        """Map the Ok value with `fn`; leave Err unchanged."""
        match self:
            case Ok(value):
                return Ok(fn(value))
            case _:
                return self

    def map_err(self, fn: Callable[[E], Any]) -> Result[T, Any]:
        """Map the Err error with `fn`; leave Ok unchanged."""
        match self:
            case Err(error):
                return Err(fn(error))
            case _:
                return self

    def bind(self, fn: Callable[[T], Result[Any, E]]) -> Result[Any, E]:
        """Flat-map: apply `fn` returning a Result if Ok; otherwise return Err."""
        match self:
            case Ok(value):
                return fn(value)
            case _:
                return self


@dataclasses.dataclass(frozen=True, slots=True)
class Ok[T, E](Result[T, E]):
    """Represents successful result containing a value."""

    __match_args__ = ("value",)
    value: T

    def __repr__(self) -> str:
        return f"Ok({self.value!r})"


@dataclasses.dataclass(frozen=True, slots=True)
class Err[T, E](Result[T, E]):
    """Represents failed result containing an error."""

    __match_args__ = ("error",)
    error: E

    def __repr__(self) -> str:
        return f"Err({self.error!r})"


def safe[**P, T](fn: Callable[P, T]) -> Callable[P, Result[T, Exception]]:
    """
    Decorator that turns a function into one returning `Result[T, Exception]`.

    - If `fn` raises an Exception, return `Err(exception)`.
    - If `fn` returns a `Result` already, return it unchanged.
    - Otherwise wrap the return value into `Ok(value)`.
    """

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Result[T, Exception]:
        try:
            result = fn(*args, **kwargs)
        except Exception as exc:
            return Err(exc)
        if isinstance(result, Result):
            return cast(Result[T, Exception], result)
        return Ok(result)

    return wrapper

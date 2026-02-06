from typing import Any, Callable


class SmarterLambda:
    def __add__(self, other: Any) -> Callable[[Any], Any]:
        return lambda x: x + other

    def __sub__(self, other: Any) -> Callable[[Any], Any]:
        return lambda x: x - other

    def __mul__(self, other: Any) -> Callable[[Any], Any]:
        return lambda x: x * other

    def __rmul__(self, other: Any) -> Callable[[Any], Any]:
        return lambda x: x * other

    def __div__(self, other: Any) -> Callable[[Any], Any]:
        return lambda x: x / other


_ = SmarterLambda()

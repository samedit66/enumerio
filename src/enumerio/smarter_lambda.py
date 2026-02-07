from typing import Any, Callable


class SmarterLambda:
    def __add__(self, other: Any) -> Callable[[Any], Any]:
        return lambda x: x + other

    def __sub__(self, other: Any) -> Callable[[Any], Any]:
        return lambda x: x - other

    def __mul__(self, other: Any) -> Callable[[Any], Any]:
        return lambda x: x * other

    def __truediv__(self, other: Any) -> Callable[[Any], Any]:
        return lambda x: x / other

    def __floordiv__(self, other: Any) -> Callable[[Any], Any]:
        return lambda x: x // other

    def __mod__(self, other: Any) -> Callable[[Any], Any]:
        return lambda x: x % other

    def __pow__(self, other: Any, modulo: Any = None) -> Callable[[Any], Any]:
        # ignoring modulo parameter for the returned lambda (rare use-case)
        return lambda x: x**other

    def __radd__(self, other: Any) -> Callable[[Any], Any]:
        return lambda x: other + x

    def __rsub__(self, other: Any) -> Callable[[Any], Any]:
        return lambda x: other - x

    def __rmul__(self, other: Any) -> Callable[[Any], Any]:
        return lambda x: other * x

    def __rtruediv__(self, other: Any) -> Callable[[Any], Any]:
        return lambda x: other / x

    def __rfloordiv__(self, other: Any) -> Callable[[Any], Any]:
        return lambda x: other // x

    def __rmod__(self, other: Any) -> Callable[[Any], Any]:
        return lambda x: other % x

    def __rpow__(self, other: Any) -> Callable[[Any], Any]:
        return lambda x: other**x

    def __iadd__(self, other: Any) -> Callable[[Any], Any]:
        return self.__add__(other)

    def __isub__(self, other: Any) -> Callable[[Any], Any]:
        return self.__sub__(other)

    def __imul__(self, other: Any) -> Callable[[Any], Any]:
        return self.__mul__(other)

    def __itruediv__(self, other: Any) -> Callable[[Any], Any]:
        return self.__truediv__(other)

    def __ifloordiv__(self, other: Any) -> Callable[[Any], Any]:
        return self.__floordiv__(other)

    def __imod__(self, other: Any) -> Callable[[Any], Any]:
        return self.__mod__(other)

    def __ipow__(self, other: Any) -> Callable[[Any], Any]:
        return self.__pow__(other)

    def __neg__(self) -> Callable[[Any], Any]:
        return lambda x: -x

    def __pos__(self) -> Callable[[Any], Any]:
        return lambda x: +x


_ = SmarterLambda()

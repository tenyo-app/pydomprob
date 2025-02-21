from collections.abc import Callable
from functools import cached_property
from inspect import getmodule, getattr_static, currentframe
from typing import Generic, ParamSpec, TypeVar

from domprob.sensors.instrums import Instruments
from domprob.sensors.meth_sig import SensorMethodSignature

# Typing helpers: Describes the wrapped method signature for wrapper
_PMeth = ParamSpec("_PMeth")
_RMeth = TypeVar("_RMeth")


class BaseSensorMethod(Generic[_PMeth, _RMeth]):
    """Base class for sensors-related methods.

    This class provides shared functionality for both
    `SensorMethod` and `BoundSensorMethod`, including
    caching and retrieval of supported instruments.

    Args:
        meth (Callable): The method associated with these sensors.
    """

    def __init__(
        self,
        meth: Callable[_PMeth, _RMeth],
        *,
        static: bool = False,
        supp_instrums: Instruments | None = None,
    ) -> None:
        self._meth = meth
        self._static = static
        self._supp_instrums = supp_instrums

    @property
    def sig(self) -> SensorMethodSignature:
        return SensorMethodSignature.from_sensor(self)

    @property
    def is_static(self) -> bool:
        cls = None
        func = self._meth
        mod = getmodule(func)
        if mod is not None:
            qualname_parts = func.__qualname__.split(".")
            obj = mod.__dict__.get(qualname_parts[0])
            for part in qualname_parts[1:-1]:
                if isinstance(obj, dict):
                    obj = obj.get(part)
                elif hasattr(obj, part):
                    obj = getattr(obj, part)
                else:
                    obj = None
            cls = obj if isinstance(obj, type) else None

        # Fallback - look in `locals()`
        # Required for dynamically created classes
        if cls is None:
            frame = currentframe()
            while frame:
                for obj in frame.f_locals.values():
                    if isinstance(obj, type) and func.__name__ in obj.__dict__:
                        cls = obj  # Found dynamically created class
                        break
                frame = frame.f_back

        if cls:
            _meth = getattr_static(cls, func.__name__, None)
            return isinstance(_meth, staticmethod)
        return False

    @property
    def meth(self) -> Callable[_PMeth, _RMeth]:
        """Returns the decorated method.

        This method represents the underlying method associated with
        the sensors.

        Returns:
            Callable[_PMeth, _RMeth]: The method associated with these
                sensors.

        Examples:
            >>> from domprob.sensors.meth import BaseSensorMethod
            >>>
            >>> def example_method():
            ...     pass
            ...
            >>> base = BaseSensorMethod(example_method)
            >>> base.meth
            <function example_method at 0x...>
        """
        return self._meth

    @cached_property
    def supp_instrums(self) -> Instruments:
        """Returns the supported instruments for this method.

        This property retrieves the metadata associated with the
        decorated method, indicating which instruments are supported.

        Returns:
            Instruments: An `Instruments` object containing metadata
                about the method’s supported instruments.

        Examples:
            >>> from domprob.sensors.meth import BaseSensorMethod
            >>>
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> def example_method(instrument: SomeInstrument) -> None:
            ...     pass
            ...
            >>> base = BaseSensorMethod(example_method)
            >>> base.supp_instrums
            Instruments(metadata=SensorMetadata(method=<function example_method at 0x...>))
        """
        return self._supp_instrums or Instruments.from_method(self.meth)

    def __repr__(self) -> str:
        """Returns a string representation of the `BaseSensor`
        instance.

        Returns:
            str: The string representation of the instance.

        Examples:
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> # Define a class with a decorated method
            >>> from domprob import sensor
            >>>
            >>> class Foo:
            ...     @sensor(SomeInstrument)
            ...     def bar(self, instrument: SomeInstrument) -> None:
            ...         pass
            ...
            >>> # Create an SensorMethod instance
            >>> bar_method = BaseSensorMethod(Foo.bar)
            >>>
            >>> repr(bar_method)
            'BaseSensorMethod(meth=<function Foo.bar at 0x...>)'
        """
        return f"{self.__class__.__name__}(meth={self.meth!r})"

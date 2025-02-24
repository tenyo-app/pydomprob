from __future__ import annotations

from collections.abc import Callable
from typing import (
    Any,
    Concatenate,
    Generic,
    ParamSpec,
    TypeVar,
)

from domprob.sensors.base_meth import BaseSensorMethod
from domprob.sensors.bound_meth import BoundSensorMethod
from domprob.sensors.instrums import Instruments
from domprob.sensors.meth_binder import SensorMethodBinder

# Typing helpers: Describes the wrapped method signature for wrapper
_PMeth = ParamSpec("_PMeth")
_RMeth = TypeVar("_RMeth")


class SensorMethod(BaseSensorMethod, Generic[_PMeth, _RMeth]):
    """Represents a decorated method with associated metadata.

    This class acts as a wrapper and provides an interface to interact
    with the supported instruments of a method decorated with
    `@sensors`. It also facilitates partially binding runtime
    arguments to the method before method execution.

    Args:
        meth (`Callable[P, R]`): The decorated method to be
            managed.

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
        >>> bar_method = SensorMethod(Foo.bar)
        >>>
        >>> bar_method
        SensorMethod(meth=<function Foo.bar at 0x...>)
    """

    __slots__: list[str] = ["_meth", "_supp_instrums", "_binder"]

    _binder: SensorMethodBinder[_PMeth, _RMeth]

    def __init__(
        self,
        meth: Callable[_PMeth, _RMeth],
        *,
        static: bool = False,
        supp_instrums: Instruments[Any] | None = None,
    ) -> None:
        super().__init__(meth, static=static, supp_instrums=supp_instrums)
        self._binder = SensorMethodBinder(self)

    @classmethod
    def from_callable(
        cls, meth: Callable[_PMeth, _RMeth]
    ) -> SensorMethod[_PMeth, _RMeth] | None:
        """Creates an `SensorMethod` instance from a callable if
        it supports instruments.

        This class method checks if the provided callable (`meth`) has
        associated metadata for supported instruments. If it does, an
        `SensorMethod` instance is created and returned.
        Otherwise, `None` is returned.

        Args:
            meth (Callable[_PMeth, _RMeth]): The method or function to
                be wrapped as an `SensorMethod`.

        Returns:
            SensorMethod[_PMeth, _RMeth] | None:
                - An instance of `SensorMethod` if the callable
                  has associated metadata.
                - `None` if the callable does not support instruments.

        Example:
            >>> from domprob import sensor
            >>>
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> class Foo:
            ...     @sensor(SomeInstrument)
            ...     def bar(self, instrument: SomeInstrument) -> None:
            ...         print(f"Instrument: {instrument}")
            ...
            >>> # Create an SensorMethod instance from a method
            >>> sensor_meth = SensorMethod.from_callable(Foo.bar)
            >>> assert isinstance(sensor_meth, SensorMethod)
            >>> print(sensor_meth)
            SensorMethod(meth=<function Foo.bar at 0x...>)

            >>> # Attempt to create an SensorMethod from a method without metadata
            >>> def no_sensor_method():
            ...     pass
            ...
            >>> assert SensorMethod.from_callable(no_sensor_method) is None
        """
        instrums = Instruments.from_method(meth)
        return cls(meth, supp_instrums=instrums) if instrums else None

    def bind(
        self, *args: _PMeth.args, **kwargs: _PMeth.kwargs
    ) -> BoundSensorMethod[Concatenate[Any, _PMeth], _RMeth]:
        # noinspection PyShadowingNames
        # pylint: disable=line-too-long
        """Binds passed parameters to the method, returning a
        partially bound version.

        This method partially binds the provided runtime arguments. It
        returns a `BoundSensorMethod` object that represents the
        partially bound method, which can later be executed with
        additional arguments if needed.

        Args:
            cls_instance (`Any`): The class instance to bind. This is
                the `self` arg defined in instance methods.
            *args (P.args): Additional positional arguments to bind to
                the method.
            **kwargs (P.kwargs): Additional keyword arguments to bind
                to the method.

        Returns:
            BoundSensorMethod: A new wrapper representing a
                partially bound method.

        Examples:
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> # Define a class with a decorated method
            >>> from domprob import sensor
            >>>
            >>> class Foo:
            ...     @sensor(SomeInstrument)
            ...     def bar(self, instrum: SomeInstrument) -> None:
            ...         pass
            ...
            >>> # Create an SensorMethod instance
            >>> bar_method = SensorMethod(Foo.bar)
            >>>
            >>> # Create an instance of the class and instrument
            >>> instrument_instance = SomeInstrument()
            >>> foo = Foo()
            >>>
            >>> # Binds method with instrument instance
            >>> args = (foo, instrument_instance)
            >>> bound_method = bar_method.bind(*args)
            >>> bound_method
            BoundSensorMethod(sensor_meth=SensorMethod(meth=<function Foo.bar at 0x...>), bound_params=<BoundArguments (self=<domprob.sensors.meth.Foo object at 0x...>, instrum=<domprob.sensors.meth.SomeInstrument object at 0x...>)>)
        """
        return self._binder.bind(*args, **kwargs)

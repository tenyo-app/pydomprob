from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Generic, ParamSpec, TypeVar

from domprob.sensors.base_meth import BaseSensorMethod
from domprob.sensors.validate.orch import SensorValidationOrchestrator

if TYPE_CHECKING:
    from domprob.sensors.meth import SensorMethod  # pragma: no cover

# Typing helpers: Describes the wrapped method signature for wrapper
_PMeth = ParamSpec("_PMeth")
_RMeth = TypeVar("_RMeth")


class BoundSensorMethod(BaseSensorMethod, Generic[_PMeth, _RMeth]):
    # pylint: disable=line-too-long
    """Represents a partially bound method with associated metadata.

    This class is used to wrap a method that has been partially bound
    with runtime arguments, including the `instrument` parameter. It
    facilitates logic, like validate, on the method with the runtime
    parameters before the method is executed.

    Args:
        sensor_meth (SensorMethod): Original method wrapper
            that's had parameters bound.
        bound_params (inspect.BoundArguments): Parameters that are
            bound to a method.

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
        >>> # Create an BoundSensorMethod instance
        >>> import inspect
        >>> from collections import OrderedDict
        >>>
        >>> from domprob.sensors.meth import SensorMethod
        >>> from domprob.sensors.bound_meth import BoundSensorMethod
        >>>
        >>> sensor_meth = SensorMethod(Foo.bar)
        >>> sig = inspect.signature(Foo.bar)
        >>> b_args = inspect.BoundArguments(sig, OrderedDict())
        >>> # Bind the arguments correctly
        >>> bound = sig.bind_partial(Foo(), SomeInstrument())
        >>> b_args.arguments = bound.arguments
        >>> bound_method = BoundSensorMethod(sensor_meth, b_args)
        >>>
        >>> bound_method
        BoundSensorMethod(sensor_meth=SensorMethod(meth=<function Foo.bar at 0x...>), bound_params=<BoundArguments (self=<domprob.sensors.bound_meth.Foo object at 0x...>, instrument=<domprob.sensors.bound_meth.SomeInstrument object at 0x...>)>)
    """

    def __init__(
        self,
        sensor_meth: SensorMethod[_PMeth, _RMeth],
        bound_params: inspect.BoundArguments,
    ) -> None:
        self._sensor_meth = sensor_meth
        self._params = bound_params
        self._validator = SensorValidationOrchestrator()
        super().__init__(
            self._sensor_meth.meth,
            static=self._sensor_meth.is_static,
            supp_instrums=self._sensor_meth.supp_instrums,
        )

    @property
    def params(self) -> inspect.BoundArguments:
        """Returns the bound arguments applied to the method.

        Returns:
            `inspect.BoundArguments`: Bound arguments applied to the
                method.

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
            >>> # Create an BoundSensorMethod instance
            >>> import inspect
            >>> from collections import OrderedDict
            >>> from domprob.sensors.meth import (
            ...     SensorMethod, BoundSensorMethod
            ... )
            >>>
            >>> sensor_meth = SensorMethod(Foo.bar)
            >>> sig = inspect.signature(Foo.bar)
            >>> b_args = inspect.BoundArguments(sig, OrderedDict())
            >>> # Bind the arguments correctly
            >>> bound = sig.bind_partial(Foo(), SomeInstrument())
            >>> b_args.arguments = bound.arguments
            >>> bound_method = BoundSensorMethod(sensor_meth, b_args)
            >>>
            >>> bound_method.instrum
            <....SomeInstrument object at 0x...>
        """
        return self._params

    @property
    def instrum(self) -> Any | None:
        """Returns the runtime `instrument` instance argument bound
        to the method.

        Returns:
            BaseInstrument: The bound `instrument` instance.

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
            >>> # Create an BoundSensorMethod instance
            >>> import inspect
            >>> from collections import OrderedDict
            >>> from domprob.sensors.meth import (
            ...     SensorMethod, BoundSensorMethod
            ... )
            >>>
            >>> sensor_meth = SensorMethod(Foo.bar)
            >>> sig = inspect.signature(Foo.bar)
            >>> b_args = inspect.BoundArguments(sig, OrderedDict())
            >>> # Bind the arguments correctly
            >>> bound = sig.bind_partial(Foo(), SomeInstrument())
            >>> b_args.arguments = bound.arguments
            >>> bound_method = BoundSensorMethod(sensor_meth, b_args)
            >>>
            >>> bound_method.instrum
            <....SomeInstrument object at 0x...>
        """
        return self.params.arguments.get("instrum")

    def execute(self) -> _RMeth:
        """Executes the bound method.

        Returns:
            R: The return value of the executed method.

        Examples:
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> # Define a class with a decorated method
            >>> from domprob import sensor
            >>>
            >>> class Foo:
            ...     @sensor(SomeInstrument)
            ...     def bar(self, instrument: SomeInstrument) -> str:
            ...         return "Executed"
            ...
            >>> # Create an BoundSensorMethod instance
            >>> import inspect
            >>> from collections import OrderedDict
            >>>
            >>> from domprob.sensors.meth import SensorMethod
            >>> from domprob.sensors.bound_meth import BoundSensorMethod
            >>>
            >>> sensor_meth = SensorMethod(Foo.bar)
            >>> sig = inspect.signature(Foo.bar)
            >>> b_args = inspect.BoundArguments(sig, OrderedDict())
            >>> # Bind the arguments correctly
            >>> bound = sig.bind_partial(Foo(), SomeInstrument())
            >>> b_args.arguments = bound.arguments
            >>> bound_method = BoundSensorMethod(sensor_meth, b_args)
            >>>
            >>> bound_method.execute()
            'Executed'
        """
        return self.meth(*self.params.args, **self.params.kwargs)

    def validate(self) -> None:
        """Validates the bound method using the validate
        orchestrator.

        This method ensures that all runtime arguments and metadata
        associated with the bound method meet the specified validate
        criteria. If validate fails, an appropriate exception is
        raised.

        Raises:
            SensorValidationException: If any validate rule
                fails.

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
            >>> # Create an BoundSensorMethod instance
            >>> import inspect
            >>> from collections import OrderedDict
            >>>
            >>> from domprob.sensors.meth import SensorMethod
            >>>
            >>> sensor_meth = SensorMethod(Foo.bar)
            >>> sig = inspect.signature(Foo.bar)
            >>> b_args = inspect.BoundArguments(sig, OrderedDict())
            >>> # Bind the arguments correctly
            >>> bound = sig.bind_partial(Foo(), SomeInstrument())
            >>> b_args.arguments = bound.arguments
            >>> bound_method = BoundSensorMethod(sensor_meth, b_args)
            >>>
            >>> # Validate the bound method
            >>> bound_method.validate()
        """
        self._validator.validate(self)

    def __repr__(self) -> str:
        # pylint: disable=line-too-long
        """Returns a string representation of the `BoundSensorMethod`
        instance.

        Returns:
            str: The string representation.

        Examples:
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> # Define a class with a decorated method
            >>> from domprob import sensor
            >>>
            >>> from domprob.sensors.meth import SensorMethod
            >>> from domprob.sensors.bound_meth import BoundSensorMethod
            >>>
            >>> class Foo:
            ...     @sensor(SomeInstrument)
            ...     def bar(self, instrument: SomeInstrument) -> str:
            ...         return "Executed"
            ...
            >>> # Create an BoundSensorMethod instance
            >>> import inspect
            >>> from collections import OrderedDict
            >>>
            >>> sensor_meth = SensorMethod(Foo.bar)
            >>> sig = inspect.signature(Foo.bar)
            >>> b_args = inspect.BoundArguments(sig, OrderedDict())
            >>> # Bind the arguments correctly
            >>> bound = sig.bind_partial(Foo(), SomeInstrument())
            >>> b_args.arguments = bound.arguments
            >>> bound_method = BoundSensorMethod(sensor_meth, b_args)
            >>>
            >>> repr(bound_method)
            'BoundSensorMethod(sensor_meth=SensorMethod(meth=<function Foo.bar at 0x...>), bound_params=<BoundArguments (self=<domprob.sensors.bound_meth.Foo object at 0x...>, instrument=<domprob.sensors.bound_meth.SomeInstrument object at 0x...>)>)'

        """
        params = (
            f"sensor_meth={self._sensor_meth!r}, "
            f"bound_params={self.params!r}"
        )
        return f"{self.__class__.__name__}({params})"

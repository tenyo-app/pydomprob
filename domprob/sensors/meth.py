from __future__ import annotations
import inspect
from collections.abc import Callable, ValuesView
from functools import cached_property
from inspect import BoundArguments, Parameter
from typing import (
    Any,
    Generic,
    ParamSpec,
    TypeVar,
    Concatenate,
    TypeAlias,
    Generator,
    get_type_hints,
)

from domprob.sensors.exc import SensorException
from domprob.sensors.instrums import Instruments
from domprob.sensors.validate.orch import SensorValidationOrchestrator


class PartialBindException(SensorException):
    # pylint: disable=line-too-long
    """Exception raised when binding arguments to a method's signature
    fails.

    This exception is used to handle errors that occur during partial
    argument binding, including missing required parameters.

    Attributes:
        meth (SensorMethod): The method whose arguments failed
            to bind.
        e (Exception): The original exception that caused the
            failure.
    """

    def __init__(self, meth: SensorMethod, e: Exception) -> None:
        self.meth = meth
        self.e = e
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        """Constructs the error message for the exception.

        The message includes the name of the method and the details of
        the original exception.

        Returns:
            str: A descriptive error message for the exception.
        """
        return f"Failed to bind parameters to {self.meth.meth!r}: {self.e}"

    def __repr__(self) -> str:
        # pylint: disable=line-too-long
        """Returns a string representation of the PartialBindException
        instance.

        The string includes the method and the original exception.

        Returns:
            str: A string representation of the exception instance.
        """
        return f"{self.__class__.__name__}(meth={self.meth!r}, e={self.e!r})"


_SensorMeth: TypeAlias = "SensorMethod[_PMeth, _RMeth]"


class SensorMethodBinder:
    """Handles argument binding for an `SensorMethod`.

    This class provides utilities for binding arguments to the method
    signature of an `SensorMethod`, both partially and fully. It
    ensures that the provided arguments match the method signature and
    raises an exception if binding fails.

    Attributes:
        sensor_meth (SensorMethod): The method wrapper
            instance for which arguments will be bound.

    Args:
        sensor_meth (SensorMethod): The method wrapper
            instance for which arguments will be bound.

    Examples:
        >>> from collections import OrderedDict
        >>> from domprob.sensors.meth import (
        ...     SensorMethod, SensorMethodBinder
        ... )
        >>>
        >>> class Foo:
        ...     def bar(self, x: int = 5) -> None:
        ...         pass
        >>>
        >>> meth = SensorMethod(Foo.bar)
        >>> binder = SensorMethodBinder(meth)
        >>> binder
        SensorMethodBinder(sensor_meth=SensorMethod(meth=<function Foo.bar at 0x...>))
    """

    _instr: str = "instrument"

    def __init__(self, sensor_meth: _SensorMeth) -> None:
        self.sensor_meth = sensor_meth

    @staticmethod
    def _apply_defaults(b_params: BoundArguments) -> BoundArguments:
        """Applies default values to bound parameters.

        This method ensures that any parameters with default values
        that were not explicitly provided during binding are assigned
        their default values.

        Args:
            b_params (BoundArguments): The bound arguments for the
                method.

        Returns:
            BoundArguments: The updated bound arguments with defaults
                applied.

        Examples:
            >>> from collections import OrderedDict
            >>> from domprob.sensors.meth import (
            ...     SensorMethod, SensorMethodBinder
            ... )
            >>>
            >>> class Foo:
            ...     def bar(self, x: int = 5) -> None:
            ...         pass
            >>>
            >>> meth = SensorMethod(Foo.bar)
            >>> binder = SensorMethodBinder(meth)
            >>>
            >>> signature = inspect.signature(Foo.bar)
            >>> b_arguments = BoundArguments(signature, OrderedDict())
            >>> b_arguments
            <BoundArguments ()>
            >>> binder._apply_defaults(b_arguments)
            <BoundArguments (x=5)>
        """
        b_params.apply_defaults()
        return b_params

    def _bind_partial(self, *args: Any, **kwargs: Any) -> BoundArguments:
        """Partially binds arguments to the method signature.

        This method allows binding a subset of the arguments required
        by the method. It does not enforce that all required parameters
        are provided.

        Args:
            *args (Any): Positional arguments to bind.
            **kwargs (Any): Keyword arguments to bind.

        Returns:
            BoundArguments: The partially bound arguments.

        Raises:
            PartialBindException: If the arguments cannot be bound to
                the method.

        Examples:
            >>> from collections import OrderedDict
            >>> from domprob.sensors.meth import (
            ...     SensorMethod, SensorMethodBinder
            ... )
            >>>
            >>> class Foo:
            ...     def bar(self, x: int, bool_: bool = True) -> None:
            ...         pass
            >>>
            >>> meth = SensorMethod(Foo.bar)
            >>> binder = SensorMethodBinder(meth)
            >>>
            >>> b_arguments = binder._bind_partial(5, bool_=False)
            >>> b_arguments
            <BoundArguments (self=5, bool_=False)>

            >>> try:
            ...     _ = binder._bind_partial(5, y=10, bool_=False)
            ... except PartialBindException:
            ...     print("Failed partial binding")
            ...
            Failed partial binding
        """
        sig = self.get_signature()
        try:
            return sig.bind_partial(*args, **kwargs)
        except TypeError as e:
            raise PartialBindException(self.sensor_meth, e) from e

    def bind(
        self, *args: Any, **kwargs: Any
    ) -> BoundSensorMethod[_PMeth, _RMeth]:
        # pylint: disable=line-too-long
        """Fully binds arguments to the method signature and returns a
        bound method.

        This method ensures that all required arguments for the method
        are bound. It applies default values where applicable and
        returns a `BoundSensorMethod` instance representing the
        method with its bound parameters.

        Args:
            *args (Any): Positional arguments to bind.
            **kwargs (Any): Keyword arguments to bind.

        Returns:
            BoundSensorMethod: A wrapper around the method with
                bound arguments.

        Raises:
            PartialBindException: If binding fails due to missing or
                incorrect arguments.

        Examples:
            >>> from collections import OrderedDict
            >>> from domprob.sensors.meth import (
            ...     SensorMethod, SensorMethodBinder
            ... )
            >>>
            >>> class Foo:
            ...     def bar(self, x: int, bool_: bool = True) -> None:
            ...         pass
            >>>
            >>> meth = SensorMethod(Foo.bar)
            >>> binder = SensorMethodBinder(meth)
            >>>
            >>> bound_meth = binder.bind(5)
            >>> bound_meth
            BoundSensorMethod(sensor_meth=SensorMethod(meth=<function Foo.bar at 0x...>), bound_params=<BoundArguments (self=5, bool_=True)>)

            >>> try:
            ...     _ = binder._bind_partial(5, y=10)
            ... except PartialBindException:
            ...     print("Failed partial binding")
            ...
            Failed partial binding
        """
        b_params = self._bind_partial(*args, **kwargs)
        b_params = self._apply_defaults(b_params)
        return BoundSensorMethod(self.sensor_meth, b_params)

    def _rn(self, param: inspect.Parameter) -> inspect.Parameter:
        return param.replace(name=self._instr)

    def _infer_ann_params(
        self, params: ValuesView[inspect.Parameter]
    ) -> Generator[Parameter, Any, None] | None:
        instrums = (i for i, _ in self.sensor_meth.supp_instrums)
        type_hints = get_type_hints(self.sensor_meth.meth)
        for param in params:
            obj = param.annotation
            if obj is inspect.Parameter.empty:  # No annotation defined
                continue
            if isinstance(obj, str):
                obj = type_hints.get(param.name)
                if obj is None:  # Can't get type from annotation
                    continue  # Should be unreachable - safety check
            if all(i for i in instrums if i == obj or issubclass(i, obj)):
                return (self._rn(p) if p is param else p for p in params)
        return None

    def _infer_pos_params(
        self, params: ValuesView[inspect.Parameter]
    ) -> Generator[inspect.Parameter, None, None]:
        params_iter = iter(params)
        try:
            first_param = next(params_iter)
        except StopIteration:
            return
        # Hacky 'self' check. This could fail if first arg in instance method
        # doesn't follow naming convention.
        if first_param.name != "self":
            first_param = self._rn(first_param)
        yield first_param
        try:
            second_param = next(params_iter)
        except StopIteration:
            return
        if first_param.name != "instrument":
            second_param = self._rn(second_param)
        yield second_param
        yield from params_iter

    def get_signature(self) -> inspect.Signature:
        """Retrieves the method signature of the wrapped
        `SensorMethod`.

        If an 'instrument' argument is not defined, manipulation
        occurs before binding to enable instrument access on the
        `BoundSensorMethod` wrapper class. The parameters in the
        method signature will change so that a parameter is renamed to
        'instrument'. In priority order, an attempt is made to
        manipulate the parameters in the following ways:

        1. The parameters type hint annotations will be inspected. It
           will check if the type hint of an argument defined in the
           method signature is the same typemor a parent type of that
           defined in all sensors decorators that wrap the
           associated method.

           .. Warning:: If multiple parameters exist that match the
              type hinting criteria above, the leftmost parameter will
              take precedence.

        2. Fallback. If neither an 'instrument' parameter is defined or
           a parameter with the correct type hint annotations are
           defined, we will assign the first parameter (exc. 'self') as
           the 'instrument' parameter.

        Returns:
            inspect.Signature: The signature of the decorated method.

        Examples:
            >>> def example_method(x: int, y: str) -> None:
            ...     pass
            ...
            >>> method = SensorMethod(example_method)
            >>> binder = SensorMethodBinder(method)
            >>> binder.get_signature()
            <Signature (instrument: 'int', y: 'str') -> 'None'>
        """
        sig = inspect.signature(self.sensor_meth.meth)
        if self._instr in sig.parameters.keys():
            return sig
        inf_params = self._infer_ann_params(sig.parameters.values())
        if inf_params is None:  # Fallback - infer instrument to be first arg
            inf_params = self._infer_pos_params(sig.parameters.values())
        return sig.replace(parameters=tuple(inf_params))

    def __repr__(self) -> str:
        # pylint: disable=line-too-long
        """Returns a string representation of the
        `SensorMethodBinder` instance.

        Returns:
            str: A string representation of the instance.

        Examples:
            >>> def example_method():
            ...     pass
            ...
            >>> method = SensorMethod(example_method)
            >>> binder = SensorMethodBinder(method)
            >>> repr(binder)
            'SensorMethodBinder(sensor_meth=SensorMethod(meth=<function example_method at 0x...>))'
        """
        return f"{self.__class__.__name__}(sensor_meth={self.sensor_meth!r})"


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
        supp_instrums: Instruments | None = None,
    ) -> None:
        self._meth = meth
        self._supp_instrums = supp_instrums

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

    def __init__(
        self,
        meth: Callable[_PMeth, _RMeth],
        supp_instrums: Instruments[Any] | None = None,
    ) -> None:
        super().__init__(meth, supp_instrums)
        self._binder = SensorMethodBinder(self)

    @classmethod
    def from_callable(
        cls, meth: Callable[_PMeth, _RMeth]
    ) -> _SensorMeth | None:
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
        supp_instrums = Instruments.from_method(meth)
        return cls(meth, supp_instrums) if supp_instrums else None

    def bind(
        self, cls_instance: Any, *args: _PMeth.args, **kwargs: _PMeth.kwargs
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
            ...     def bar(self, instrument: SomeInstrument) -> None:
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
            BoundSensorMethod(sensor_meth=SensorMethod(meth=<function Foo.bar at 0x...>), bound_params=<BoundArguments (self=<domprob.sensors.meth.Foo object at 0x...>, instrument=<domprob.sensors.meth.SomeInstrument object at 0x...>)>)
        """
        return self._binder.bind(cls_instance, *args, **kwargs)


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
        >>> from collections import OrderedDict
        >>> sensor_meth = SensorMethod(Foo.bar)
        >>> sig = inspect.signature(Foo.bar)
        >>> b_args = BoundArguments(sig, OrderedDict())
        >>> # Bind the arguments correctly
        >>> bound = sig.bind_partial(Foo(), SomeInstrument())
        >>> b_args.arguments = bound.arguments
        >>> bound_method = BoundSensorMethod(sensor_meth, b_args)
        >>>
        >>> bound_method
        BoundSensorMethod(sensor_meth=SensorMethod(meth=<function Foo.bar at 0x...>), bound_params=<BoundArguments (self=<domprob.sensors.meth.Foo object at 0x...>, instrument=<domprob.sensors.meth.SomeInstrument object at 0x...>)>)
    """

    def __init__(
        self,
        sensor_meth: SensorMethod[_PMeth, _RMeth],
        bound_params: inspect.BoundArguments,
    ) -> None:
        super().__init__(sensor_meth.meth)
        self._sensor_meth = sensor_meth
        self._params = bound_params
        self._validator = SensorValidationOrchestrator()

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
            ...     def bar(self, instrument: SomeInstrument) -> None:
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
            >>> b_args = BoundArguments(sig, OrderedDict())
            >>> # Bind the arguments correctly
            >>> bound = sig.bind_partial(Foo(), SomeInstrument())
            >>> b_args.arguments = bound.arguments
            >>> bound_method = BoundSensorMethod(sensor_meth, b_args)
            >>>
            >>> bound_method.instrument
            <....SomeInstrument object at 0x...>
        """
        return self._params

    @property
    def instrument(self) -> Any | None:
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
            ...     def bar(self, instrument: SomeInstrument) -> None:
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
            >>> b_args = BoundArguments(sig, OrderedDict())
            >>> # Bind the arguments correctly
            >>> bound = sig.bind_partial(Foo(), SomeInstrument())
            >>> b_args.arguments = bound.arguments
            >>> bound_method = BoundSensorMethod(sensor_meth, b_args)
            >>>
            >>> bound_method.instrument
            <....SomeInstrument object at 0x...>
        """
        return self.params.arguments.get("instrument")

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
            >>> from collections import OrderedDict
            >>> sensor_meth = SensorMethod(Foo.bar)
            >>> sig = inspect.signature(Foo.bar)
            >>> b_args = BoundArguments(sig, OrderedDict())
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
            ...     def bar(self, instrument: SomeInstrument) -> None:
            ...         pass
            ...
            >>> # Create an BoundSensorMethod instance
            >>> from collections import OrderedDict
            >>> sensor_meth = SensorMethod(Foo.bar)
            >>> sig = inspect.signature(Foo.bar)
            >>> b_args = BoundArguments(sig, OrderedDict())
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
            >>> class Foo:
            ...     @sensor(SomeInstrument)
            ...     def bar(self, instrument: SomeInstrument) -> str:
            ...         return "Executed"
            ...
            >>> # Create an BoundSensorMethod instance
            >>> from collections import OrderedDict
            >>> sensor_meth = SensorMethod(Foo.bar)
            >>> sig = inspect.signature(Foo.bar)
            >>> b_args = BoundArguments(sig, OrderedDict())
            >>> # Bind the arguments correctly
            >>> bound = sig.bind_partial(Foo(), SomeInstrument())
            >>> b_args.arguments = bound.arguments
            >>> bound_method = BoundSensorMethod(sensor_meth, b_args)
            >>>
            >>> repr(bound_method)
            'BoundSensorMethod(sensor_meth=SensorMethod(meth=<function Foo.bar at 0x...>), bound_params=<BoundArguments (self=<domprob.sensors.meth.Foo object at 0x...>, instrument=<domprob.sensors.meth.SomeInstrument object at 0x...>)>)'

        """
        params = (
            f"sensor_meth={self._sensor_meth!r}, "
            f"bound_params={self.params!r}"
        )
        return f"{self.__class__.__name__}({params})"

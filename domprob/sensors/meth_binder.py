from __future__ import annotations
import inspect
from collections.abc import Generator, ValuesView
from typing import (
    get_type_hints,
    Any,
    ParamSpec,
    TypeAlias,
    TypeVar,
    TYPE_CHECKING,
    Generic,
)

from domprob.sensors.exc import SensorException
from domprob.sensors.bound_meth import BoundSensorMethod

# Typing helpers: Describes the wrapped method signature for wrapper
_PMeth = ParamSpec("_PMeth")
_RMeth = TypeVar("_RMeth")


if TYPE_CHECKING:
    from domprob.sensors.meth import SensorMethod  # pragma: no cover

    _SensorMeth: TypeAlias = SensorMethod[_PMeth, _RMeth]  # pragma: no cover
    _BoundSensorMeth: TypeAlias = BoundSensorMethod[
        _PMeth, _RMeth
    ]  # pragma: no cover


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

    def __init__(
        self, meth: SensorMethod[_PMeth, _RMeth], e: Exception
    ) -> None:
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


class SensorMethodBinder(Generic[_PMeth, _RMeth]):
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
        >>> from domprob.sensors.meth import SensorMethod
        >>> from domprob.sensors.meth_binder import SensorMethodBinder
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
    def _apply_defaults(
        b_params: inspect.BoundArguments,
    ) -> inspect.BoundArguments:
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
            >>> import inspect
            >>> from collections import OrderedDict
            >>> from domprob.sensors.meth import SensorMethod
            >>> from domprob.sensors.meth_binder import SensorMethodBinder
            >>>
            >>> class Foo:
            ...     def bar(self, x: int = 5) -> None:
            ...         pass
            >>>
            >>> meth = SensorMethod(Foo.bar)
            >>> binder = SensorMethodBinder(meth)
            >>>
            >>> signature = inspect.signature(Foo.bar)
            >>> b_arguments = inspect.BoundArguments(signature, OrderedDict())
            >>> b_arguments
            <BoundArguments ()>
            >>> binder._apply_defaults(b_arguments)
            <BoundArguments (x=5)>
        """
        b_params.apply_defaults()
        return b_params

    def _bind_partial(
        self, *args: Any, **kwargs: Any
    ) -> inspect.BoundArguments:
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
            >>> from domprob.sensors.meth import SensorMethod
            >>> from domprob.sensors.meth_binder import SensorMethodBinder
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

    def bind(self, *args: Any, **kwargs: Any) -> _BoundSensorMeth:
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
            >>> from domprob.sensors.meth import SensorMethod
            >>> from domprob.sensors.meth_binder import SensorMethodBinder
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
    ) -> Generator[inspect.Parameter, Any, None] | None:
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
            >>> from domprob.sensors.meth import SensorMethod
            >>>
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
            >>> from domprob.sensors.meth import SensorMethod
            >>>
            >>> def example_method():
            ...     pass
            ...
            >>> method = SensorMethod(example_method)
            >>> binder = SensorMethodBinder(method)
            >>> repr(binder)
            'SensorMethodBinder(sensor_meth=SensorMethod(meth=<function example_method at 0x...>))'
        """
        return f"{self.__class__.__name__}(sensor_meth={self.sensor_meth!r})"

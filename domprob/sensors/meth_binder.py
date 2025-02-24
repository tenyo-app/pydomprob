from __future__ import annotations

import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    ParamSpec,
    TypeAlias,
    TypeVar,
)

from domprob.sensors.bound_meth import BoundSensorMethod
from domprob.sensors.exc import SensorException
from domprob.sensors.meth_sig import SensorMethodSignature

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

    def __init__(self, sensor_meth: _SensorMeth) -> None:
        self.sensor_meth = sensor_meth

    def _bind_partial(
        self,
        sig: SensorMethodSignature[_PMeth, _RMeth],
        *args: Any,
        **kwargs: Any,
    ) -> inspect.BoundArguments:
        # noinspection PyShadowingNames
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
            >>> from domprob.sensors.meth_sig import SensorMethodSignature
            >>>
            >>> class Foo:
            ...     def bar(self, x: int, bool_: bool = True) -> None:
            ...         pass
            >>>
            >>> meth = SensorMethod(Foo.bar)
            >>> binder = SensorMethodBinder(meth)
            >>> sig = SensorMethodSignature.from_sensor(meth)
            >>>
            >>> b_arguments = binder._bind_partial(sig, 5, bool_=False)
            >>> b_arguments
            <BoundArguments (self=5, bool_=False)>

            >>> try:
            ...     _ = binder._bind_partial(sig, 5, y=10, bool_=False)
            ... except PartialBindException:
            ...     print("Failed partial binding")
            ...
            Failed partial binding
        """
        try:
            return sig.bind_partial(*args, **kwargs)
        except TypeError as e:
            raise PartialBindException(self.sensor_meth, e) from e

    def bind(self, *args: Any, **kwargs: Any) -> _BoundSensorMeth:
        # pylint: disable=line-too-long
        # noinspection PyShadowingNames
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
            >>> from domprob.sensors.meth_sig import SensorMethodSignature
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

            >>> sig = SensorMethodSignature.from_sensor(meth)
            >>> try:
            ...     _ = binder._bind_partial(sig, 5, y=10)
            ... except PartialBindException:
            ...     print("Failed partial binding")
            ...
            Failed partial binding
        """
        sig = self.sensor_meth.sig.infer()
        b_params = self._bind_partial(sig, *args, **kwargs)
        b_params.apply_defaults()
        return BoundSensorMethod(self.sensor_meth, b_params)

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

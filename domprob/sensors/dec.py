import functools
from collections.abc import Callable
from typing import (
    Any,
    Concatenate,
    Generic,
    ParamSpec,
    TypeAlias,
    TypeVar,
    overload,
)

from domprob.sensors.meth import SensorMethod

# Typing helper: Describes the class where the method resides
_MethodCls = TypeVar("_MethodCls", bound=Any)

# Typing helper: Describes the instrument parameter
_Instrum = TypeVar("_Instrum", bound=Any)

# Typing helpers: Describes the method signature
_P = ParamSpec("_P")
_R = TypeVar("_R")

_InstanceMeth: TypeAlias = Callable[Concatenate[_MethodCls, _Instrum, _P], _R]
_StaticMeth: TypeAlias = Callable[Concatenate[_Instrum, _P], _R]
_Meth: TypeAlias = _InstanceMeth | _StaticMeth


class _Sensor(Generic[_MethodCls, _Instrum, _P, _R]):
    """Decorator class for associating metadata and validating methods.

    This class enables the decoration of methods with metadata
    describing their required instruments. It enforces runtime
    validate to ensure that the method is called with the correct
    parameters and that the `instrument` argument satisfies the
    specified requirements.

    The `@sensors` decorator can be stacked.

    .. warning::
       It is strongly recommended that instrument classes defined in
       stacked decorators inherit from the same base class or
       implement the same typing protocol.

    Args:
        instrum (type[_Instrum]): The instrument class required
            by the decorated method.
        required (bool): Whether the instrument is required. Defaults
            to `False`.

    Examples:

        Simple implementation:

        >>> class PrintInstrument:
        ...
        ...     @staticmethod
        ...     def stdout(msg: str) -> None:
        ...         print(msg)
        ...
        ...     def __repr__(self) -> str:
        ...         return f"{self.__class__.__name__}()"
        ...
        >>> # Define a class with a decorated method
        >>> from domprob import sensor
        >>>
        >>> class Foo:
        ...     @sensor(PrintInstrument)
        ...     def bar(self, instrument: PrintInstrument) -> None:
        ...         instrument.stdout(f"Executing with {instrument!r}")
        ...
        >>> foo = Foo()
        >>> instru = PrintInstrument()
        >>>
        >>> foo.bar(instru)
        Executing with PrintInstrument()

        Supporting the same sensors implementation with multiple
        instruments:

        >>> import logging
        >>> from abc import ABC, abstractmethod
        >>>
        >>> # Define instruments
        >>> class AbstractStdOutInstrument(ABC):
        ...     @abstractmethod
        ...     def stdout(self, cls_name: str) -> None:
        ...         raise NotImplementedError
        ...
        ...     def __repr__(self) -> str:
        ...         return f"{self.__class__.__name__}()"
        ...
        >>> class PrintInstrument(AbstractStdOutInstrument):
        ...     def stdout(self, cls_name: str) -> None:
        ...         print(f"Observing '{cls_name}' with '{self!r}'\")
        ...
        >>> class LogInstrument(AbstractStdOutInstrument):
        ...
        ...     def __init__(self):
        ...         self.logger = logging.getLogger()
        ...         self.logger.setLevel(logging.INFO)
        ...
        ...     def stdout(self, cls_name: str) -> None:
        ...         logger = logging.getLogger()
        ...         logger.setLevel(logging.INFO)
        ...         logger.info(f"Observing '{cls_name}' with '{self!r}'\")
        ...
        >>> # Define a class with a decorated method
        >>> from domprob import sensor
        >>>
        >>> class Foo:
        ...     @sensor(PrintInstrument)
        ...     @sensor(LogInstrument)
        ...     def bar(self, instrument: AbstractStdOutInstrument) -> None:
        ...         instrument.stdout(self.__class__.__name__)
        ...
        >>> foo = Foo()
        >>> instru = PrintInstrument()
        >>>
        >>> foo.bar(instru)
        Observing 'Foo' with 'PrintInstrument()'
    """

    def __init__(
        self, instrum: type[_Instrum], required: bool = False
    ) -> None:
        self.instrum = instrum
        self.required = required

    @overload
    def __call__(self, method: _StaticMeth) -> _StaticMeth: ...

    @overload
    def __call__(self, method: _InstanceMeth) -> _InstanceMeth: ...

    def __call__(self, method: _Meth) -> _Meth:
        """Wraps a method to associate metadata and enforce runtime
        validate.

        This method is invoked when the `@sensors` decorator is
        used on a method. It attaches metadata, including the
        instrument class and requirement status, to the method and
        enforces validate when the method is called at runtime.

        Args:
            method (Callable[P, R]): The method to decorate.

        Returns:
            Callable[P, R]: A wrapped version of the input method with
            metadata and validate applied.

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
            ...         print(f"Executing with {instrument!r}")
            ...
            >>> foo = Foo()
            >>> instru = SomeInstrument()
            >>>
            >>> foo.bar(instru)
            Executing with <...SomeInstrument object at 0x...>
        """

        meth = SensorMethod(method)
        meth.supp_instrums.record(self.instrum, self.required)

        @overload
        def wrapper(  # noqa - ignore "unused local function" warning
            instrum: _Instrum, /, *args: _P.args, **kwargs: _P.kwargs
        ) -> _R: ...

        @overload
        def wrapper(  # noqa - ignore "unused local function" warning
            cls_instance: _MethodCls,
            instrum: _Instrum,
            /,
            *args: _P.args,
            **kwargs: _P.kwargs,
        ) -> _R: ...

        @functools.wraps(method)
        def wrapper(*args: Any, **kwargs: Any) -> _R:
            bound_meth = meth.bind(*args, **kwargs)
            bound_meth.validate()
            return bound_meth.execute()

        return wrapper

    def __repr__(self) -> str:
        # noinspection PyShadowingNames
        """Returns a string representation of the `_Sensor`
        instance.

        This method provides a concise, informative string
        representation of the `_Sensor` instance, including its
        instrument class and requirement status.

        Returns:
            str: A string representation of the `_Sensor` instance.

        Examples:
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> sensor = _Sensor(SomeInstrument)
            >>> repr(sensor)
            "_Sensor(instrum=<class '...SomeInstrument'>)"
        """
        return f"{self.__class__.__name__}(instrum={self.instrum!r})"


# pylint: disable=invalid-name
sensor = _Sensor  # Alias to be pythonic

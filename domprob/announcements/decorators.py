import functools
from collections.abc import Callable
from typing import (
    Any,
    Generic,
    ParamSpec,
    TypeVar,
    cast,
    Concatenate,
)

from domprob.announcements.method import AnnouncementMethod

# Typing helper: Describes the class where the method resides
_MethodCls = TypeVar("_MethodCls", bound=Any)

# Typing helper: Describes the instrument parameters
_Instrument = TypeVar("_Instrument", bound=Any)

# Typing helpers: Describes the method signature
_P = ParamSpec("_P")
_R = TypeVar("_R")
_Meth = Callable[Concatenate[_MethodCls, _Instrument, _P], _R]


class _Announcement(Generic[_MethodCls, _Instrument, _P, _R]):
    """Decorator class for associating metadata and validating methods.

    This class enables the decoration of methods with metadata
    describing their required instruments. It enforces runtime
    validation to ensure that the method is called with the correct
    parameters and that the `instrument` argument satisfies the
    specified requirements.

    The `@announcement` decorator can be stacked.

    .. warning::
       It is strongly recommended that instrument classes defined in
       stacked decorators inherit from the same base class or
       implement the same typing protocol.

    Args:
        instrument (type[_Instrument]): The instrument class required
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
        >>> from domprob import announcement
        >>>
        >>> class Foo:
        ...     @announcement(PrintInstrument)
        ...     def bar(self, instrument: PrintInstrument) -> None:
        ...         instrument.stdout(f"Executing with {instrument!r}")
        ...
        >>> foo = Foo()
        >>> instru = PrintInstrument()
        >>>
        >>> foo.bar(instru)
        Executing with PrintInstrument()

        Supporting the same announcement implementation with multiple
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
        >>> from domprob import announcement
        >>>
        >>> class Foo:
        ...     @announcement(PrintInstrument)
        ...     @announcement(LogInstrument)
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
        self, instrument: type[_Instrument], required: bool = False
    ) -> None:
        self.instrument = instrument
        self.required = required

    def __call__(self, method: _Meth) -> Callable[_P, _R]:
        """Wraps a method to associate metadata and enforce runtime
        validation.

        This method is invoked when the `@announcement` decorator is
        used on a method. It attaches metadata, including the
        instrument class and requirement status, to the method and
        enforces validation when the method is called at runtime.

        Args:
            method (Callable[P, R]): The method to decorate.

        Returns:
            Callable[P, R]: A wrapped version of the input method with
            metadata and validation applied.

        Examples:
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> # Define a class with a decorated method
            >>> from domprob import announcement
            >>>
            >>> class Foo:
            ...     @announcement(SomeInstrument)
            ...     def bar(self, instrument: SomeInstrument) -> None:
            ...         print(f"Executing with {instrument!r}")
            ...
            >>> foo = Foo()
            >>> instru = SomeInstrument()
            >>>
            >>> foo.bar(instru)
            Executing with <...SomeInstrument object at 0x...>
        """

        meth = AnnouncementMethod(method)
        meth.supp_instrums.record(self.instrument, self.required)

        @functools.wraps(method)
        def wrapper(
            cls_instance: _MethodCls,
            instrument: _Instrument,
            /,
            *args: _P.args,
            **kwargs: _P.kwargs,
        ) -> _R:
            bound_meth = meth.bind(cls_instance, instrument, *args, **kwargs)
            bound_meth.validate()
            return bound_meth.execute()

        return cast(Callable[_P, _R], wrapper)

    def __repr__(self) -> str:
        # noinspection PyShadowingNames
        """Returns a string representation of the `Announcement`
        instance.

        This method provides a concise, informative string
        representation of the `Announcement` instance, including its
        instrument class and requirement status.

        Returns:
            str: A string representation of the `Announcement` instance.

        Examples:
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> announcement = _Announcement(SomeInstrument)
            >>> repr(announcement)
            "_Announcement(instrument=<class '...SomeInstrument'>)"
        """
        return f"{self.__class__.__name__}(instrument={self.instrument!r})"


# pylint: disable=invalid-name
announcement = _Announcement  # Alias to be pythonic

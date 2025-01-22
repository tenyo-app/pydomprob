"""
announcements.py
===============

This module provides utilities for managing metadata associated with
decorated methods, specifically for `@announcements` functionality. It
facilitates the handling of metadata entries, validation of instrument
requirements, and execution of decorated methods with type safety.

Key Classes:
-------------
- `AnnoMetadataItem`: Represents a single metadata entry for a method,
  including the associated instrument type and its requirement status.
- `AnnoMetadata`: Manages metadata entries for decorated methods,
  supporting operations such as addition, iteration, and validation.
- `Instruments`: Provides a high-level interface to interact with
  instruments associated with a method's metadata.
- `AnnoMethod` and `InstrumentBoundAnnoMethod`: Represent methods with
  metadata binding and support validation workflows.
- `AnnoValidatorChainBuilder`: Implements a chain of responsibility
  pattern for validator execution.
- `Announcement`: The main decorator class, enabling the addition of
  metadata and runtime validation to methods.

Usage:
-------
Decorate a method with `@announcements` to associate metadata and enforce
instrument requirements at runtime. Use the `AnnoMetadata` and `Instruments`
classes to manage and query metadata programmatically.

Example:
--------
>>> from domprob.instrument import BaseInstrument
>>> class Foo:
...     @announcements(BaseInstrument, required=True)
...     def bar(self, instrument):
...         print(f\"Executing with {instrument!r}\")
>>> foo = Foo()
>>> foo.bar(instrument=BaseInstrument())
Executing with BaseInstrument()
"""

import functools
from collections.abc import Callable
from typing import Any, Generic, ParamSpec, TypeAlias, TypeVar

from domprob.announcements.method import AnnouncementMethod
from domprob.announcements.validation.orchestrator import (
    AnnouncementValidationOrchestrator,
)

_InstruCls: TypeAlias = type[Any]

# Type variables for InstrumentBoundAnnoMethod
_P = ParamSpec("_P")
_R = TypeVar("_R")
_Wrapped: TypeAlias = Callable[_P, _R]


class _Announcement(Generic[_P, _R]):
    """Decorator class to add metadata and validate methods.

    This class is used to decorate methods and associate metadata,
    such as the required instrument type, with those methods. It
    provides runtime validation to ensure that the method is called
    with the correct parameters and that the `instrument` argument
    meets the specified requirements.

    @announcements decorators can also be stacked. Note: It's strongly
    advised instrument classes defined in stacked announcements
    decorators inherit from the same base class.

    Args:
        instrument (TInstruCls): The instrument class that
            the decorated method expects.
        required (`bool`, optional): Indicates whether the instrument
            is required during method execution. Defaults to `True`.

    Examples:
        >>> class Foo:
        ...     @announcement(BaseInstrument)  # Defaults to required=True
        ...     def bar(self, instrument: BaseInstrument) -> None:
        ...         print(f\"Executing with {instrument!r}\")
        ...
        >>> foo = Foo()
        >>> foo.bar(instrument=BaseInstrument())
        Executing with BaseInstrument()

        >>> from abc import ABC, abstractmethod
        >>> from typing import Any
        >>> import logging
        >>>
        >>> class AbstractStdOutInstrument(ABC, BaseInstrument):
        ...     @abstractmethod
        ...     def stdout(self, cls: Any) -> None:
        ...         raise NotImplementedError
        ...
        >>> class PrintInstrument(AbstractStdOutInstrument):
        ...     def stdout(self, cls: Any) -> None:
        ...         print(f"Observing '{cls!r}' with '{self!r}'\")
        ...
        >>> class LogInstrument(AbstractStdOutInstrument):
        ...     def stdout(self, cls: Any) -> None:
        ...         logger = logging.getLogger()
        ...         logger.setLevel(logging.INFO)
        ...         logger.info(f"Observing '{cls!r}' with '{self!r}'\")
        ...
        >>> class Foo:
        ...     @announcement(PrintInstrument)
        ...     @announcement(LogInstrument)
        ...     def bar(self, instrument: AbstractStdOutInstrument) -> None:
        ...         instrument.stdout(self.__class__.__name__)
        ...
        >>> foo = Foo()
        >>> foo.bar(PrintInstrument())
        Stdout with 'PrintInstrument()' from class 'Foo'
    """

    def __init__(self, instrument: _InstruCls) -> None:
        self.instrument = instrument
        self.required = True

    def __call__(self, method: _Wrapped) -> _Wrapped:
        """Wraps a method to associate metadata and enforce runtime
        validation.

        This method is invoked when the `@announcements` decorator is used
        on a method. It attaches metadata, including the instrument class
        and requirement status, to the method and enforces validation when
        the method is called at runtime.

        Args:
            method (`Callable[P, R]`): The method to decorate.

        Returns:
            Callable[P, R]: A wrapped version of the input method with
            metadata and validation applied.

        Examples:
            >>> class Foo:
            ...     @announcements(BaseInstrument)
            ...     def bar(self, instrument: BaseInstrument):
            ...         print(f\"Instrument: {instrument!r}\")
            ...
            >>> foo = Foo()
            >>> foo.bar(instrument=BaseInstrument())
            Instrument: BaseInstrument()
        """
        # Ensure the metadata is applied to the original method
        while hasattr(method, "__wrapped__"):
            method = getattr(method, "__wrapped__")
        meth = AnnouncementMethod(method)
        meth.instruments.record(self.instrument, self.required)

        @functools.wraps(method)
        def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _R:
            bound_meth = meth.bind(*args, **kwargs)
            self.validater.validate(bound_meth)
            result = bound_meth.execute()
            return result

        return wrapper

    @property
    def validater(self):
        return AnnouncementValidationOrchestrator()

    def __repr__(self) -> str:
        """Returns a string representation of the `Announcement`
        instance.

        This method provides a concise, informative string
        representation of the `Announcement` instance, including its
        instrument class and requirement status.

        Returns:
            str: A string representation of the `Announcement` instance.

        Examples:
            >>> ann = _Announcement(BaseInstrument, required=True)
            >>> repr(ann)
            "Announcement(instrument=BaseInstrument, required=True)"
        """
        return (
            f"{self.__class__.__name__}(instrument={self.instrument!r}, "
            f"required={self.required})"
        )


# pylint: disable=invalid-name
announcement = _Announcement  # Alias to be pythonic

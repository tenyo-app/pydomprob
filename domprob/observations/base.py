from __future__ import annotations
import inspect
from abc import ABC
from collections.abc import Generator
from functools import cached_property
from typing import ParamSpec, TypeVar, Generic, Any

from domprob.announcements.method import AnnouncementMethod
from domprob.observations.observation import ObservationProtocol

# Typing helpers: defines an @announcement method signature
_P = ParamSpec("_P")
_R = TypeVar("_R")
_AnnounceSig = AnnouncementMethod[_P, _R]
_Instrument = TypeVar("_Instrument", bound=Any)

_PROPERTY_TYPES = (property, cached_property)


def _is_function(obj: object) -> bool:
    """Check if an object is a function that is not a property or
    dunder method.

    Args:
        obj (object): The object to check.

    Returns:
        bool: True if the object is a regular function, False
            otherwise.

    Example:
        >>> def example_func(): pass
        >>> _is_function(example_func)
        True

        >>> class Example:
        ...     @property
        ...     def prop(self): return 42
        ...
        >>> _is_function(Example.prop)
        False
    """
    return (
        inspect.isfunction(obj)
        and not isinstance(obj, _PROPERTY_TYPES)
        and not (obj.__name__.startswith("__") and obj.__name__.endswith("__"))
    )


class BaseObservation(
    ABC, Generic[_P, _R, _Instrument], ObservationProtocol[[Any, Any], Any]
):
    """Base class for observations.

    Attributes:
        __slots__ (tuple): Prevents the creation of instance __dict__
            to keep memory footprint low.

    Example:
        >>> from domprob import announcement, BaseObservation
        >>>
        >>> class SomeInstrument:
        ...     pass
        ...
        >>> class MyObservation(BaseObservation):
        ...     @announcement(SomeInstrument)
        ...     def my_method(self, instrument: SomeInstrument) -> str:
        ...         pass
        ...
        >>> observation = MyObservation()
        >>> observation
        MyObservation(announcements=1)
    """

    # cached per observation sub cls - avoids recompute for each instance
    _announcements: list[_AnnounceSig] | None = None

    @classmethod
    def announcements(cls) -> Generator[_AnnounceSig, None, None]:
        """Yield announcement methods defined in the class.

        Uses **lazy evaluation** to avoid unnecessary memory
        consumption.

        Yields:
            _AnnounceSig: Announcement method instances.

        Example:
            >>> from domprob import announcement, BaseObservation
            >>>
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> class MyObservation(BaseObservation):
            ...     @announcement(SomeInstrument)
            ...     def event_occurred(self, instrument: SomeInstrument) -> None:
            ...         pass
            ...
            >>> gen = MyObservation.announcements()
            >>> list(gen)
            [AnnouncementMethod(meth=<function MyObservation.event_occurred at 0x...>)]
        """
        if cls._announcements is not None:
            yield from cls._announcements
            return
        announce_meths = []
        for _, meth in inspect.getmembers(cls, predicate=_is_function):
            announce_meth = AnnouncementMethod.from_callable(meth)
            if announce_meth is not None:
                announce_meths.append(announce_meth)
                yield announce_meth
        cls._announcements = announce_meths

    def __len__(self) -> int:
        """Return the number of announcements.

        Returns:
            int: Count of announcements in the class.

        Example:
            >>> from domprob import announcement, BaseObservation
            >>>
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> class MyObservation(BaseObservation):
            ...     @announcement(SomeInstrument)
            ...     def my_method(self, instrument: SomeInstrument) -> str:
            ...         pass
            ...
            >>> observation = MyObservation()
            >>> len(observation)
            1
        """
        return len(list(self.announcements()))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(announcements={len(self)})"

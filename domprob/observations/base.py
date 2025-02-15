from __future__ import annotations
import inspect
from abc import ABC
from collections.abc import Generator, Set
from typing import ParamSpec, TypeVar, Any

from domprob.announcements.method import AnnouncementMethod
from domprob.observations.observation import ObservationProtocol

# Typing helpers: defines an @announcement method signature
_P = ParamSpec("_P")
_R = TypeVar("_R")
_AnnounceSig = AnnouncementMethod[_P, _R]


class AnnouncementSet(Set):
    """A custom set-like collection for storing `AnnouncementMethod`
    instances.

    This class ensures unique announcement methods and provides
    set-like behavior for iteration, containment checks, and length
    retrieval.

    Args:
        *announcement_methods (_AnnounceSig): One or more announcement
            method instances.

    Example:
        >>> from domprob import announcement
        >>>
        >>> class MyObservation:
        ...
        ...     @announcement(...)
        ...     def announce_hello(self, _):
        ...         pass
        ...
        ...     def normal_method(self, _):
        ...         pass
        ...
        >>> meth = AnnouncementMethod(MyObservation.announce_hello)
        >>> announcement_set = AnnouncementSet(meth, meth)
        >>> len(announcement_set)
        1
    """

    def __init__(self, *announcement_methods: _AnnounceSig) -> None:
        self._announcement_methods = set(announcement_methods)

    @classmethod
    def from_observation(cls, observation_cls: Any) -> AnnouncementSet:
        """Creates an AnnouncementSet by extracting announcement
        methods from a given class.

        This method inspects the provided class, identifies methods
        that qualify as announcement methods using
        `AnnouncementMethod.from_callable`, and includes them in the
        returned `AnnouncementSet`.

        Args:
            observation_cls (Any): The class to inspect for
                announcement methods.

        Returns:
            AnnouncementSet: A set of extracted announcement methods.

        Example:
            >>> from domprob import announcement
            >>>
            >>> class MyObservation:
            ...
            ...     @announcement(...)
            ...     def announce_hello(self, _):
            ...         pass
            ...
            ...     def normal_method(self, _):
            ...         pass
            ...
            >>> announcement_set = AnnouncementSet.from_observation(MyObservation)
            >>> len(announcement_set)
            1
        """
        meths = []
        for _, meth in inspect.getmembers(observation_cls, inspect.isfunction):
            announce_meth = AnnouncementMethod.from_callable(meth)
            if announce_meth is not None:
                meths.append(announce_meth)
        return cls(*meths)

    def __contains__(self, item: Any) -> bool:
        """Checks if a given announcement method exists in the set.

        Args:
            item (Any): The item to check.

        Returns:
            bool: True if `item` is an instance of `AnnouncementMethod`
                and exists in the set, False otherwise.
        """
        if not isinstance(item, AnnouncementMethod):
            return False
        return item in self._announcement_methods

    def __iter__(self) -> Generator[_AnnounceSig, None, None]:
        """Returns an iterator over the announcement methods in the
        set.

        Yields:
            _AnnounceSig: Each announcement method stored in the set.
        """
        yield from self._announcement_methods

    def __len__(self) -> int:
        """Returns the number of announcement methods in the set.

        Returns:
            int: The count of stored announcement methods.
        """
        return len(self._announcement_methods)

    def __repr__(self) -> str:
        """Returns a string representation of the AnnouncementSet.

        Returns:
            str: A string describing the number of stored
                announcements.
        """
        return f"{self.__class__.__name__}(num_announcements={len(self)})"


class BaseObservation(ABC, ObservationProtocol):
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

    # cached per observation cls imp - avoids recompute for each instance
    _announcements: AnnouncementSet | None = None

    @classmethod
    def announcements(cls) -> AnnouncementSet:
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
        if cls._announcements is None:
            cls._announcements = AnnouncementSet.from_observation(cls)
        return cls._announcements

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

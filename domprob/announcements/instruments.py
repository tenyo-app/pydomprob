from __future__ import annotations
from collections.abc import Callable, Generator
from typing import Any, TypeVar, Generic

from domprob.announcements.metadata import AnnouncementMetadata

# Typing helpers
_InstruCls = TypeVar("_InstruCls", bound=type[Any])
_InstrumentClsGen = Generator[_InstruCls, None, None]
_InstrumentTupleClsGen = Generator[tuple[_InstruCls, bool], None, None]


class Instruments(Generic[_InstruCls]):
    """Manages and provides access to instrument classes for a
    decorated method's metadata.

    Args:
        metadata (`AnnouncementMetadata`): The metadata object managing
            the associated method's metadata.

    Examples:
        >>> # Define a class with a method
        >>> class Foo:
        ...     def bar(self):
        ...         pass
        ...
        >>> # Create metadata for the method
        >>> from domprob.announcements import metadata
        >>> meta = metadata.AnnouncementMetadata(Foo.bar)
        >>>
        >>> # Access metadata instruments
        >>> from domprob.announcements.instruments import Instruments
        >>> instruments = Instruments(meta)
        >>>
        >>> instruments
        Instruments(metadata=AnnouncementMetadata(method=<function Foo.bar at 0x...>))
    """

    def __init__(self, metadata: AnnouncementMetadata) -> None:
        self._metadata = metadata

    def __iter__(self) -> _InstrumentTupleClsGen:
        """Iterates over all instruments.

        Yields:
            _InstrumentTupleClsGen: Instrument classes associated with
                the method's metadata.

        Examples:
            >>> # Define a class with a method to decorate
            >>> class Foo:
            ...     def bar(self):
            ...         pass
            ...
            >>> # Create instruments handler for method
            >>> from domprob.announcements.instruments import Instruments
            >>> instruments = Instruments.from_method(Foo.bar)
            >>>
            >>> # Define an instrument
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> instruments.record(SomeInstrument, True)
            Instruments(metadata=AnnouncementMetadata(method=<function Foo.bar at 0x...>))
            >>> list(instruments)
            [(<class 'domprob.announcements.instruments.SomeInstrument'>, True)]
        """
        yield from ((m.instrument_cls, m.required) for m in self._metadata)

    def __len__(self) -> int:
        """Returns the number of instrument entries associated with
        the method's metadata.

        This method provides the total count of all instrument classes
        recorded in the metadata for the associated method.

        Returns:
            int: The total number of instrument classes recorded.

        Examples:
            >>> # Define a class with a method to decorate
            >>> class Foo:
            ...     def bar(self):
            ...         pass
            ...
            >>> # Create instruments handler for method
            >>> from domprob.announcements.instruments import Instruments
            >>> instruments = Instruments.from_method(Foo.bar)
            >>> # Initially, no instruments are recorded
            >>> len(instruments)
            0
            >>> # Define an instrument
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> # Record the instrument
            >>> instruments.record(SomeInstrument, required=True)
            Instruments(metadata=AnnouncementMetadata(method=<function Foo.bar at 0x...>))
            >>> len(instruments)
            1
        """
        return len(self._metadata)

    def __eq__(self, other: Any) -> bool:
        """
        Checks equality between the current `Instruments` instance and
        another object.

        This method determines whether the provided object is an
        instance of `Instruments` and whether their associated
        metadata are equal. Two `Instruments` instances ar considered
        equal if they manage the same `AnnouncementMetadata`.

        Args:
            other (Any): The object to compare with the current
                `Instruments` instance.

        Returns:
            bool: `True` if the provided object is an `Instruments`
                instance and their metadata are equal.

        Examples:
            >>> # Define a class with a method
            >>> class Foo:
            ...     def bar(self):
            ...         pass
            ...
            >>> # Create Instruments instances for the same method
            >>> from domprob.announcements.instruments import Instruments
            >>> instruments1 = Instruments.from_method(Foo.bar)
            >>> instruments2 = Instruments.from_method(Foo.bar)
            >>>
            >>> instruments1 == instruments2
            True

            >>> # Create Instruments instance for a different method
            >>> class Baz:
            ...     def qux(self):
            ...         pass
            ...
            >>> instruments3 = Instruments.from_method(Baz.qux)
            >>> instruments1 == instruments3
            False

            >>> # Compare with an unrelated object
            >>> instruments1 == "Not an Instruments instance"
            False
        """
        if not isinstance(other, Instruments):
            return False
        return self._metadata == other._metadata

    @classmethod
    def from_method(cls, method: Callable[..., Any]) -> Instruments:
        """Creates an Instruments instance from a method.

        Provides a convenient way to initialise an `Instruments`
        object directly from a method without explicitly creating an
        `AnnoMetadata` instance.

        Args:
            method (`Callable[..., Any]`): The method for which the
                instruments should be managed.

        Returns:
            Instruments: An `Instruments` instance for managing the
                method's metadata.

        Examples:
            >>> # Define a class with a method to decorate
            >>> class Foo:
            ...     def bar(self):
            ...         pass
            ...
            >>> # Create an Instruments instance directly from the method
            >>> from domprob.announcements.instruments import Instruments
            >>> instruments = Instruments.from_method(Foo.bar)
            >>> instruments
            Instruments(metadata=AnnouncementMetadata(method=<function Foo.bar at 0x...>))
        """
        return cls(AnnouncementMetadata(method))

    @property
    def non_req_instrums(self) -> _InstrumentClsGen:
        """Generator yielding supported instrument classes marked as
        not required in the method's metadata.

        Yields:
            TInstrumentClsGen: Non-required instrument classes.

        Examples:
            >>> # Define a class with a method to decorate
            >>> class Foo:
            ...     def bar(self):
            ...         pass
            ...
            >>> # Create an Instruments instance directly from the method
            >>> from domprob.announcements.instruments import Instruments
            >>> instruments = Instruments.from_method(Foo.bar)
            >>>
            >>> # Define an instrument class
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> # Add a required instrument
            >>> instruments.record(SomeInstrument, required=True)
            Instruments(metadata=AnnouncementMetadata(method=<function Foo.bar at 0x...>))
            >>>
            >>> list(instruments.non_req_instrums)
            []
            >>> instruments.record(SomeInstrument, required=False)
            Instruments(metadata=AnnouncementMetadata(method=<function Foo.bar at 0x...>))
            >>> list(instruments.non_req_instrums)
            [<class '...SomeInstrument'>]
        """
        yield from (m.instrument_cls for m in self._metadata if not m.required)

    @property
    def req_instrums(self) -> _InstrumentClsGen:
        """Generator yielding supported instrument classes marked as
        required in the method's metadata.

        Yields:
            TInstrumentClsGen: Required instrument classes.

        Examples:
            >>> # Define a class with a method to decorate
            >>> class Foo:
            ...     def bar(self):
            ...         pass
            ...
            >>> # Create an Instruments instance directly from the method
            >>> from domprob.announcements.instruments import Instruments
            >>> instruments = Instruments.from_method(Foo.bar)
            >>>
            >>> # Define an instrument class
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> instruments.record(SomeInstrument, required=False)
            Instruments(metadata=AnnouncementMetadata(method=<function Foo.bar at 0x...>))
            >>> list(instruments.req_instrums)
            []
            >>> instruments.record(SomeInstrument, required=True)
            Instruments(metadata=AnnouncementMetadata(method=<function Foo.bar at 0x...>))
            >>> list(instruments.req_instrums)
            [<class '...SomeInstrument'>]
        """
        yield from (m.instrument_cls for m in self._metadata if m.required)

    def is_required(self, instrument_cls: _InstruCls) -> bool:
        """Checks if any recorded instrument of the same instrument
        type given is required.

        Args:
            instrument_cls (`TInstruCls`): The instrument type to
                check against the method's metadata.

        Returns:
            bool: `True` if any instrument of the given type is marked
                as required, otherwise `False`.

        Examples:
            >>> # Define a class with a method to decorate
            >>> class Foo:
            ...     def bar(self):
            ...         pass
            ...
            >>> # Create instruments handler for method
            >>> from domprob.announcements.instruments import Instruments
            >>> instruments = Instruments.from_method(Foo.bar)
            >>>
            >>> # Define an instrument class
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> instruments.is_required(SomeInstrument)
            False
            >>> instruments.record(SomeInstrument, False)
            Instruments(metadata=AnnouncementMetadata(method=<function Foo.bar at 0x...>))
            >>> instruments.record(SomeInstrument, True)
            Instruments(metadata=AnnouncementMetadata(method=<function Foo.bar at 0x...>))
            >>> instruments.is_required(SomeInstrument)
            True
        """
        for instru in self._metadata:
            if (instru.instrument_cls is instrument_cls) and instru.required:
                return True  # return early if required instrument found
        return False

    def record(self, instrument: _InstruCls, required: bool) -> "Instruments":
        """Adds an instrument entry to the method's metadata.

        Args:
            instrument (type[`BaseInstrument`]): The instrument class
                to add to the method's metadata.
            required (`bool`): Whether the instrument is required.

        Returns:
            Instruments: The updated `Instruments` instance.

        Examples:
            >>> # Define a class with a method to decorate
            >>> class Foo:
            ...     def bar(self):
            ...         pass
            ...
            >>> # Create instruments handler for the method
            >>> from domprob.announcements.instruments import Instruments
            >>> instruments = Instruments.from_method(Foo.bar)
            >>>
            >>> # Define an instrument class
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> # Add a required instrument
            >>> instruments.record(SomeInstrument, required=True)
            Instruments(metadata=AnnouncementMetadata(method=<function Foo.bar at 0x...>))
            >>> # Add a non-required instrument
            >>> instruments.record(SomeInstrument, required=False)
            Instruments(metadata=AnnouncementMetadata(method=<function Foo.bar at 0x...>))
        """
        self._metadata.add(instrument, required)
        return self

    def supported(self, required: bool | None = None) -> _InstrumentClsGen:
        """Yields supported instrument classes filtered by requirement.

        Args:
            required (`bool`, optional): If `True`, yields only
                required instruments. If `False`, yields only
                non-required instruments. If `None`, yields all
                instruments. Defaults to `None`.

        Yields:
            TInstrumentClsGen: Instrument classes that match the
                filter criteria.

        Examples:
            >>> # Define a class with a method to decorate
            >>> class Foo:
            ...     def bar(self):
            ...         pass
            ...
            >>> # Create instruments handler for method
            >>> from domprob.announcements.instruments import Instruments
            >>> instruments = Instruments.from_method(Foo.bar)
            >>>
            >>> # Define an instrument class
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> # Add instruments
            >>> instruments.record(SomeInstrument, required=True)
            Instruments(metadata=AnnouncementMetadata(method=<function Foo.bar at 0x...>))
            >>>
            >>> # Filter instruments based on their requirement status
            >>> list(instruments.supported(True))
            [<class '...SomeInstrument'>]
            >>> list(instruments.supported(False))
            []
            >>> instruments.record(SomeInstrument, required=False)
            Instruments(metadata=AnnouncementMetadata(method=<function Foo.bar at 0x...>))
            >>> list(instruments.supported())
            [<class '...SomeInstrument'>, <class '...SomeInstrument'>]
        """
        if required is None:
            yield from (m.instrument_cls for m in self._metadata)
        elif not required:
            yield from self.non_req_instrums
        else:
            yield from self.req_instrums

    def __repr__(self) -> str:
        """Returns a string representation of the Instruments instance.

        Returns:
            str: The string representation of the Instruments object.

        Examples:
            >>> # Define a class with a method to decorate
            >>> class Foo:
            ...     def bar(self):
            ...         pass
            ...
            >>> # Create instruments handler for method
            >>> from domprob.announcements.instruments import Instruments
            >>> instruments = Instruments.from_method(Foo.bar)
            >>> repr(instruments)
            'Instruments(metadata=AnnouncementMetadata(method=<function Foo.bar at 0x...>))'
        """
        return f"{self.__class__.__name__}(metadata={self._metadata!r})"

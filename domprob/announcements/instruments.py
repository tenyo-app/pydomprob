from collections.abc import Callable, Generator
from typing import Any

from domprob.announcements.metadata import AnnouncementMetadata
from domprob.instrument import BaseInstrument

# Typing helpers
TInstruCls = type[BaseInstrument]
TInstrumentClsGen = Generator[TInstruCls, None, None]


class Instruments:
    """Manages and provides access to instrument classes for a
    decorated method's metadata.

    Args:
        metadata (`AnnoMetadata`): The metadata object managing
            the associated method's metadata.

    Examples:
        >>> # Define a class with a method to decorate
        >>> class Foo:
        ...     def bar(self):
        ...         pass
        ...
        >>> # Create metadata for the method
        >>> metadata = AnnouncementMetadata(Foo.bar)
        >>> # Abstract metadata instrument access
        >>> instruments = Instruments(metadata)
        >>> instruments
        Instruments(metadata=AnnoMetadata(Foo.bar))
    """

    def __init__(self, metadata: AnnouncementMetadata) -> None:
        self._metadata = metadata

    def __iter__(self) -> TInstrumentClsGen:
        """Iterates over all supported instrument classes.

        Yields:
            TInstrumentClsGen: Instrument classes associated with
                the method's metadata.

        Examples:
            >>> # Define a class with a method to decorate
            >>> class Foo:
            ...     def bar(self):
            ...         pass
            ...
            >>> # Create instruments handler for method
            >>> instruments = Instruments.from_method(Foo.bar)
            >>> instruments.record(BaseInstrument)
            >>> list(instruments)
            [BaseInstrument]
        """
        yield from (m.instrument_cls for m in self._metadata)

    def __len__(self) -> int:
        return len(self._metadata)

    @classmethod
    def from_method(cls, method: Callable[..., Any]) -> "Instruments":
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
            >>> instruments = Instruments.from_method(Foo.bar)
            >>> instruments
            Instruments(metadata=AnnoMetadata(Foo.bar))
        """
        return cls(AnnouncementMetadata(method))

    @property
    def non_req_instruments(self) -> TInstrumentClsGen:
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
            >>> instruments = Instruments.from_method(Foo.bar)
            >>> # Add a required instrument
            >>> instruments.record(BaseInstrument, True)
            >>>
            >>> list(instruments.non_req_instruments)
            []
        """
        yield from (m.instrument_cls for m in self._metadata if not m.required)

    @property
    def req_instruments(self) -> TInstrumentClsGen:
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
            >>> instruments = Instruments.from_method(Foo.bar)
            >>> # Add a non-required entry to the method's metadata
            >>> instruments.record(BaseInstrument, False)
            >>>
            >>> list(instruments.req_instruments)
            []
        """
        yield from (m.instrument_cls for m in self._metadata if m.required)

    def is_required(self, instrument_cls: TInstruCls) -> bool:
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
            >>> instruments = Instruments.from_method(Foo.bar)
            >>> # Record a required instrument
            >>> instruments.record(BaseInstrument, True)
            >>> instruments.record(BaseInstrument, False)
            >>> instruments.is_required(BaseInstrument)
            True
        """
        for instru in self._metadata:
            if (instru.instrument_cls is instrument_cls) and instru.required:
                return True  # return early if required instrument found
        return False

    def record(
        self, instrument: TInstruCls, required: bool = True
    ) -> "Instruments":
        """Adds an instrument entry to the method's metadata.

        Args:
            instrument (type[`BaseInstrument`]): The instrument class
                to add to the method's metadata.
            required (`bool`, optional): Whether the instrument is
                required. Defaults to `True`.

        Returns:
            Instruments: The updated `Instruments` instance.

        Examples:
            >>> # Define a class with a method to decorate
            >>> class Foo:
            ...     def bar(self):
            ...         pass
            ...
            >>> # Create instruments handler for method
            >>> instruments = Instruments.from_method(Foo.bar)
            >>> instruments.record(BaseInstrument, True)
            >>> list[instruments]
            [BaseInstrument]
        """
        self._metadata.add(instrument, required)
        return self

    def supported(self, required: bool | None = None) -> TInstrumentClsGen:
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
            >>> instruments = Instruments.from_method(Foo.bar)
            >>> # Add instruments
            >>> instruments.record(BaseInstrument, True)
            >>> instruments.record(BaseInstrument, False)
            >>>
            >>> list(instruments.supported(required=True))
            [BaseInstrument]
            >>> list(instruments.supported(required=False))
            [BaseInstrument]
            >>> list(instruments.supported())
            [BaseInstrument, BaseInstrument]
        """
        if required is None:
            yield from self
        elif not required:
            yield from self.non_req_instruments
        yield from self.req_instruments

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
            >>> instruments = Instruments.from_method(Foo.bar)
            >>> repr(instruments)
            "Instruments(metadata=AnnoMetadata(Foo.bar))"
        """
        return f"{self.__class__.__name__}(metadata={self._metadata!r})"

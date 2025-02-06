from collections.abc import Callable, Generator
from dataclasses import dataclass
from typing import Any


@dataclass
class AnnouncementMetadataEntry:
    """Represents metadata entry for an announcement's method. Includes
    the instrument class and its requirement status.

    Args:
        instrument_cls (type[`BaseInstrument`]): The type of
            instrument for which the announcements should be executed.
        required (`bool`), optional: Whether the instrument instance
            at runtime is required or optional for the announcements.
            Defaults to `True` if not provided during instantiation.

    Examples:
        >>> class SomeInstrument:
        ...     pass
        ...
        >>> # Define a class with a method
        >>> class Foo:
        ...     def bar(self):
        ...         pass
        ...
        >>> # Create metadata for the method
        >>> from domprob.announcements import metadata
        >>> entry = metadata.AnnouncementMetadataEntry(SomeInstrument, required=False)
        >>> entry
        AnnouncementMetadataEntry(instrument_cls=<class '...SomeInstrument'>, required=False)
        >>> entry.instrument_cls
        <class '...SomeInstrument'>
        >>> entry.required
        False
    """

    instrument_cls: type[Any]
    required: bool = True


class AnnouncementMetadata:
    """Stores and manages metadata for an instance method.

    Args:
        method (`Callable[..., Any]`): The method for which the
            metadata is to be managed.

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
        >>> meta
        AnnouncementMetadata(method=<function Foo.bar at 0x...>)
    """

    # The attribute name where the metadata will be saved to on the
    # method.
    METADATA_ATTR: str = "__announcement_metadata__"

    def __init__(self, method: Callable[..., Any]) -> None:
        while hasattr(method, "__wrapped__"):  # Get original non-wrapped
            method = getattr(method, "__wrapped__")
        self._method = method

    def __len__(self) -> int:
        """Returns the number of metadata entries.

        Returns:
            int: The number of metadata entries recorded for the
                method.

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
            >>> len(meta)
            0
            >>> # Define an instrument
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> meta.add(SomeInstrument, required=True)
            AnnouncementMetadata(method=<function Foo.bar at 0x...>)
            >>> len(meta)
            1
        """
        return len(getattr(self._method, self.METADATA_ATTR, []))

    def __iter__(self) -> Generator[AnnouncementMetadataEntry, None, None]:
        """Iterates over all metadata entries recorded for the method.

        Yields:
            AnnoMetadataItem: Metadata items associated with the
                method.

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
            >>> # Define an instrument
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> # Add entries to the metadata
            >>> meta.add(SomeInstrument, True).add(SomeInstrument, False)
            AnnouncementMetadata(method=<function Foo.bar at 0x...>)
            >>>
            >>> meta_iter = iter(meta)
            >>> next(meta_iter)
            AnnouncementMetadataEntry(instrument_cls=<class '...SomeInstrument'>, required=True)
            >>> next(meta_iter)
            AnnouncementMetadataEntry(instrument_cls=<class '...SomeInstrument'>, required=False)
        """
        yield from tuple(getattr(self._method, self.METADATA_ATTR, []))

    def __eq__(self, other: Any) -> bool:
        """Equality operator to check if two `AnnouncementMetadata`
        instances are equivalent.

        Args:
            other (Any): The object to compare with the current
                `AnnouncementMetadata` instance. Typically expected
                to be another `AnnouncementMetadata` object.

        Returns:
            bool: Returns `True` if both operands reference the
                metadata of the same instance method

        Examples:
            >>> # Define a class with a method
            >>> class Foo:
            ...     def bar(self):
            ...         pass
            ...
            >>> # Create metadata for the method
            >>> from domprob.announcements import metadata
            >>> meta_1 = metadata.AnnouncementMetadata(Foo.bar)
            >>> meta_1 == "string"
            False
            >>> meta_2 = metadata.AnnouncementMetadata(Foo.bar)
            >>> meta_1 == meta_2
            True
            >>>
            >>> # Define an instrument
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> meta_1.add(SomeInstrument, True)
            AnnouncementMetadata(method=<function Foo.bar at 0x...>)
            >>> meta_1 == meta_2  # Both reference the same method
            True
        """
        if not isinstance(other, AnnouncementMetadata):
            return False
        return self._method == other._method

    def add(self, instrument: Any, required: bool) -> "AnnouncementMetadata":
        """Adds an announcements metadata entry to the method.

        Args:
            instrument (type[`BaseInstrument`]): The instrument class
                to add to the method's metadata.
            required (`bool`): Whether the instrument is required.

        Returns:
            AnnouncementMetadata: The updated metadata instance.

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
            >>> len(meta)
            0
            >>> # Define an instrument
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> meta.add(SomeInstrument, required=True)
            AnnouncementMetadata(method=<function Foo.bar at 0x...>)
            >>> len(meta)
            1
        """
        item = AnnouncementMetadataEntry(instrument, required=required)
        meth_metadata = list(self)
        meth_metadata.append(item)
        setattr(self._method, self.METADATA_ATTR, meth_metadata)
        return self

    def __repr__(self) -> str:
        """Returns a string representation of the metadata instance.

        Returns:
            str: The string representation.

        Examples:
            >>> # Define a class with a method to decorate
            >>> class Foo:
            ...     def bar(self):
            ...         pass
            ...
            >>> # Create metadata for the method
            >>> from domprob.announcements import metadata
            >>> meta = metadata.AnnouncementMetadata(Foo.bar)
            >>> repr(meta)
            'AnnouncementMetadata(method=<function Foo.bar at 0x...>)'
        """
        return f"{self.__class__.__name__}(method={self._method!r})"

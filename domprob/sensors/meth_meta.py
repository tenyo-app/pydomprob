from collections.abc import Callable, Generator
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SensorMetadataEntry:
    """Represents metadata entry for a sensors' method. Includes
    the instrument class and its requirement status.

    Args:
        instrument_cls (type[`BaseInstrument`]): The type of
            instrument for which the sensors should be executed.
        required (`bool`), optional: Whether the instrument instance
            at runtime is required or optional for the sensors.
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
        >>> from domprob.sensors import meth_meta
        >>> entry = meth_meta.SensorMetadataEntry(SomeInstrument, required=False)
        >>> entry
        SensorMetadataEntry(instrument_cls=<class '...SomeInstrument'>, required=False)
        >>> entry.instrument_cls
        <class '...SomeInstrument'>
        >>> entry.required
        False
    """

    instrument_cls: type[Any]
    required: bool


class SensorMetadata:
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
        >>> from domprob.sensors import meth_meta
        >>> meta = meth_meta.SensorMetadata(Foo.bar)
        >>>
        >>> meta
        SensorMetadata(method=<function Foo.bar at 0x...>)
    """

    # The attribute name where the metadata will be saved to on the
    # method.
    METADATA_ATTR: str = "__sensor_metadata__"

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
            >>> from domprob.sensors import meth_meta
            >>> meta = meth_meta.SensorMetadata(Foo.bar)
            >>>
            >>> len(meta)
            0
            >>> # Define an instrument
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> meta.add(SomeInstrument, required=True)
            SensorMetadata(method=<function Foo.bar at 0x...>)
            >>> len(meta)
            1
        """
        return len(getattr(self._method, self.METADATA_ATTR, []))

    def __iter__(self) -> Generator[SensorMetadataEntry, None, None]:
        """Iterates over all metadata entries recorded for the method.

        Yields:
            SensorMetadataEntry: Metadata items associated with the
                method.

        Examples:
            >>> # Define a class with a method
            >>> class Foo:
            ...     def bar(self):
            ...         pass
            ...
            >>> # Create metadata for the method
            >>> from domprob.sensors import meth_meta
            >>> meta = meth_meta.SensorMetadata(Foo.bar)
            >>>
            >>> # Define an instrument
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> # Add entries to the metadata
            >>> meta.add(SomeInstrument, True).add(SomeInstrument, False)
            SensorMetadata(method=<function Foo.bar at 0x...>)
            >>>
            >>> meta_iter = iter(meta)
            >>> next(meta_iter)
            SensorMetadataEntry(instrument_cls=<class '...SomeInstrument'>, required=True)
            >>> next(meta_iter)
            SensorMetadataEntry(instrument_cls=<class '...SomeInstrument'>, required=False)
        """
        yield from tuple(getattr(self._method, self.METADATA_ATTR, []))

    def __eq__(self, other: Any) -> bool:
        """Equality operator to check if two `SensorMetadata`
        instances are equivalent.

        Args:
            other (Any): The object to compare with the current
                `SensorMetadata` instance. Typically expected
                to be another `SensorMetadata` object.

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
            >>> from domprob.sensors import meth_meta
            >>> meta_1 = meth_meta.SensorMetadata(Foo.bar)
            >>> meta_1 == "string"
            False
            >>> meta_2 = meth_meta.SensorMetadata(Foo.bar)
            >>> meta_1 == meta_2
            True
            >>>
            >>> # Define an instrument
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> meta_1.add(SomeInstrument, True)
            SensorMetadata(method=<function Foo.bar at 0x...>)
            >>> meta_1 == meta_2  # Both reference the same method
            True
        """
        if not isinstance(other, SensorMetadata):
            return False
        return self._method == other._method

    def add(self, instrument: Any, required: bool) -> "SensorMetadata":
        """Adds a sensors' metadata entry to the method.

        Args:
            instrument (type[`BaseInstrument`]): The instrument class
                to add to the method's metadata.
            required (`bool`): Whether the instrument is required.

        Returns:
            SensorMetadata: The updated metadata instance.

        Examples:
            >>> # Define a class with a method
            >>> class Foo:
            ...     def bar(self):
            ...         pass
            ...
            >>> # Create metadata for the method
            >>> from domprob.sensors import meth_meta
            >>> meta = meth_meta.SensorMetadata(Foo.bar)
            >>>
            >>> len(meta)
            0
            >>> # Define an instrument
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> meta.add(SomeInstrument, required=True)
            SensorMetadata(method=<function Foo.bar at 0x...>)
            >>> len(meta)
            1
        """
        item = SensorMetadataEntry(instrument, required=required)
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
            >>> from domprob.sensors import meth_meta
            >>> meta = meth_meta.SensorMetadata(Foo.bar)
            >>> repr(meta)
            'SensorMetadata(method=<function Foo.bar at 0x...>)'
        """
        return f"{self.__class__.__name__}(method={self._method!r})"

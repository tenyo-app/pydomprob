"""
metadata.py
===========

This module provides classes and utilities for managing metadata associated
with decorated methods. It is designed to facilitate the handling of
metadata entries, which include instrument types and their requirement
status, as part of a method's runtime behaviour.

Key Features
------------
- `AnnoMetadataItem`: Represents a single metadata entry, encapsulating
  an instrument class and its requirement status (required or optional).
- `AnnoMetadata`: Manages metadata for methods, supporting operations such
  as adding metadata entries, iterating over entries, and retrieving the
  number of entries.

Classes
-------
- `AnnoMetadataItem`: A dataclass to store details about individual metadata
  items.
- `AnnoMetadata`: A utility class for managing collections of metadata items
  for specific methods.

Usage
-----
Decorate methods with metadata and manage their metadata programmatically.
`AnnoMetadata` allows for the addition, retrieval, and iteration of metadata
entries associated with methods.

Example
-------
>>> from domprob.announcements import metadata
>>>
>>> class Foo:
...     def bar(self):
...         pass
...
>>> # Create metadata for the method
>>> meta = metadata.AnnoMetadata(Foo.bar)
>>> meta.add(BaseInstrument, req=True)
>>> list(meta)
[AnnoMetadataItem(instrument_cls=BaseInstrument, required=True)]
"""

from collections.abc import Callable, Generator
from dataclasses import dataclass
from typing import Any, TypeAlias

from domprob.instrument import BaseInstrument

_InstruCls: TypeAlias = type[BaseInstrument]


@dataclass
class AnnoMetadataItem:
    """Represents metadata entry for an announcement's method. Includes
    the instrument class and its requirement status.

    Args:
        instrument_cls (type[`BaseInstrument`]): The type of
            instrument for which the announcements should be executed.
        required (`bool`), optional: Whether the instrument instance
            at runtime is required or optional for the announcements.
            Defaults to `True` if not provided during instantiation.

    Examples:
        >>> item = AnnoMetadataItem(BaseInstrument, required=False)
        >>> item
        AnnoMetadataItem(instrument_cls=BaseInstrument, required=False)
        >>> item.instrument_cls
        <class 'BaseInstrument'>
        >>> item.required
        False

        >>> item = AnnoMetadataItem(BaseInstrument)
        >>> item
        AnnoMetadataItem(instrument_cls=BaseInstrument, required=True)
        >>> item.required
        True
    """

    instrument_cls: _InstruCls
    required: bool = True


class AnnoMetadata:
    """Stores and manages metadata for a decorated method.

    Args:
        method (`Callable[..., Any]`): The method for which the
            metadata is to be managed.

    Examples:
        >>> # Define a class with a method to decorate
        >>> class Foo:
        ...     def bar(self):
        ...         pass
        ...
        >>> # Create metadata for the method
        >>> metadata = AnnoMetadata(Foo.bar)
        >>> metadata
        AnnoMetadata(method=Foo.bar)
    """

    # The attribute name where the metadata will be saved to on the
    # method.
    METADATA_ATTR: str = "__announcement_metadata__"

    def __init__(self, method: Callable[..., Any]) -> None:
        self._method = method

    def __len__(self) -> int:
        """Returns the number of metadata entries.

        Returns:
            int: The number of metadata entries recorded for the
                method.

        Examples:
            >>> # Define a class with a method to decorate
            >>> class Foo:
            ...     def bar(self):
            ...         pass
            ...
            >>> # Create metadata for the method
            >>> metadata = AnnoMetadata(Foo.bar)
            >>>
            >>> len(metadata)
            0
            >>> metadata.add(BaseInstrument)
            >>> len(metadata)
            1
        """
        return len(self)

    def __iter__(self) -> Generator[AnnoMetadataItem, None, None]:
        """Iterates over all metadata entries recorded for the method.

        Yields:
            AnnoMetadataItem: Metadata items associated with the
                method.

        Examples:
            >>> # Define a class with a method to decorate
            >>> class Foo:
            ...     def bar(self):
            ...         pass
            ...
            >>> # Create metadata for the method
            >>> metadata = AnnoMetadata(Foo.bar)
            >>> # Add entries to the metadata
            >>> metadata.add(BaseInstrument, True)
            >>> metadata.add(BaseInstrument, False)
            >>>
            >>> list(metadata)
            [
                AnnoMetadataItem(instrument_cls=BaseInstrument, required=True),
                AnnoMetadataItem(instrument_cls=BaseInstrument, required=False)
            ]
        """
        yield from tuple(getattr(self._method, self.METADATA_ATTR, []))

    def add(self, instrument: _InstruCls, required: bool) -> "AnnoMetadata":
        """Adds an announcements metadata entry to the method.

        Args:
            instrument (type[`BaseInstrument`]): The instrument class
                to add to the method's metadata.
            required (`bool`): Whether the instrument is required.

        Returns:
            AnnoMetadata: The updated metadata instance.

        Examples:
            >>> # Define a class with a method to decorate
            >>> class Foo:
            ...     def bar(self):
            ...         pass
            ...
            >>> # Create metadata for the method
            >>> metadata = AnnoMetadata(Foo.bar)
            >>> len(metadata)
            0
            >>> # Add an entry to the method's metadata
            >>> metadata.add(BaseInstrument, req=True)
            >>> len(metadata)
            1
        """
        item = AnnoMetadataItem(instrument, required=required)
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
            >>> metadata = AnnoMetadata(Foo.bar)
            >>> repr(metadata)
            "AnnoMetadata(metadata=Foo.bar)"
        """
        return f"{self.__class__.__name__}(metadata={self._method!r})"

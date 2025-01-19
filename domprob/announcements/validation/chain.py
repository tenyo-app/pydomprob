from abc import ABC, abstractmethod
from collections.abc import Generator, Iterable, MutableSequence
from operator import index as to_index
from typing import (Any, Generic, ParamSpec, SupportsIndex, TypeAlias, TypeVar,
                    overload)

from domprob.announcements.exceptions import AnnouncementException
from domprob.announcements.validation.base_validator import \
    BaseAnnouncementValidator

# Ensures base must be a concrete class implementing the protocol
_ChainLink = TypeVar("_ChainLink", bound=BaseAnnouncementValidator)

# Type alias for the chain
_Chain: TypeAlias = "ValidationChain"


class ValidationChainException(AnnouncementException):
    """Base exception for validation chain-related errors."""


class InvalidLinkException(ValidationChainException):
    """Exception raised when a link is invalid."""

    def __init__(self, link: Any, base: type[_ChainLink]) -> None:
        self.link = link
        self.base = base
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        l_name = type(self.link).__name__
        b_name = self.base.__name__
        return f"Invalid link of type '{l_name}', expected type '{b_name}'"


class EmptyChainException(ValidationChainException):
    """Exception raised when attempting to validate an empty chain."""

    def __init__(self, chain: _Chain) -> None:
        self.chain = chain
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        return f"Nothing to validate, no links added to chain '{self.chain!r}'"


class LinkExistsException(ValidationChainException):
    """Exception raised when attempting to validate an empty chain."""

    def __init__(self, link: _ChainLink, chain: _Chain) -> None:
        self.link = link
        self.chain = chain
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        return f"Link '{self.link!r}' already exists in chain '{self.chain!r}'"


# Represent `@_validate_link` wrapped method
_P = ParamSpec("_P")
_R = TypeVar("_R")


# pylint: disable=too-few-public-methods
class ABCLinkValidator(ABC):
    def __init__(self, chain: _Chain) -> None:
        self.chain = chain

    @abstractmethod
    def validate(self, link: _ChainLink) -> None:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.chain!r})"


class LinkTypeValidator(ABCLinkValidator):
    def validate(self, link: _ChainLink) -> None:
        if not isinstance(link, self.chain.base):
            raise InvalidLinkException(link, self.chain.base)


class UniqueLinkValidator(ABCLinkValidator):
    def validate(self, link: _ChainLink) -> None:
        if link in self.chain:
            raise LinkExistsException(link, self.chain)


class ABCLinkValidatorContext(ABC):

    def __init__(
        self, chain: _Chain, *validators: type[ABCLinkValidator]
    ) -> None:
        self.chain = chain
        self.validators: list[type[ABCLinkValidator]] = list(*validators)
        self.add_validators(*validators)

    @abstractmethod
    def add_validators(self, *validators: type[ABCLinkValidator]) -> None:
        raise NotImplementedError

    @abstractmethod
    def validate(self, link: _ChainLink) -> None:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class LinkValidatorContext(ABCLinkValidatorContext):

    DEFAULT_VALIDATORS: list[type[ABCLinkValidator]] = [
        LinkTypeValidator,
        UniqueLinkValidator,
    ]

    def __init__(
        self, chain: _Chain, *validators: type[ABCLinkValidator]
    ) -> None:
        super().__init__(chain, *self.DEFAULT_VALIDATORS, *validators)

    def add_validators(self, *validators: type[ABCLinkValidator]) -> None:
        self.validators.extend(validators)

    def validate(self, *links: _ChainLink) -> None:
        for validator in self.validators:
            for link in links:
                validator(self.chain).validate(link)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.chain!r})"


class ValidationChain(Generic[_ChainLink], MutableSequence[_ChainLink]):

    def __init__(
        self,
        base: type[_ChainLink],
        *link_validators: type[ABCLinkValidator],
        validator_context: ABCLinkValidatorContext | None = None,
    ) -> None:
        self.base = base
        self._links: list[_ChainLink] = []
        self._link_validator = validator_context or LinkValidatorContext(
            self, *link_validators
        )

    def __bool__(self) -> bool:
        return bool(self._links)

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, self.base):
            return False
        return item in self._links

    def __delitem__(self, index: SupportsIndex | slice, /) -> None:
        if isinstance(index, slice):
            self._delete_slice_items(index)
        elif isinstance(index, int):
            self._delete_single_item(to_index(index))
        else:
            raise TypeError(f"Invalid index type: {type(index).__name__}")

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ValidationChain):
            return False
        return self._links == other._links

    @overload
    # need to match the superclasses overloaded signatures exactly
    def __getitem__(self, index: int, /) -> _ChainLink: ...

    @overload
    # need to match the superclasses overloaded signatures exactly
    def __getitem__(self, index: slice, /) -> MutableSequence[_ChainLink]: ...

    def __getitem__(
        self, index: int | slice, /
    ) -> _ChainLink | MutableSequence[_ChainLink]:
        return self._links[index]

    def __iter__(self) -> Generator[_ChainLink, None, None]:
        yield from self._links

    def __len__(self) -> int:
        return len(self._links)

    @overload
    # need to match the superclasses overloaded signatures exactly
    def __setitem__(self, index: int, link: _ChainLink, /) -> None: ...

    @overload
    # need to match the superclasses overloaded signatures exactly
    def __setitem__(
        self, index: slice, links: Iterable[_ChainLink], /
    ) -> None: ...

    def __setitem__(
        self,
        index: SupportsIndex | slice,
        link_or_links: _ChainLink | Iterable[_ChainLink],
        /,
    ) -> None:
        if isinstance(index, slice):
            if not isinstance(link_or_links, Iterable):
                raise TypeError("Expected an iterable for slice assignment")
            self._set_slice_items(index, link_or_links)
        elif isinstance(index, SupportsIndex):
            if isinstance(link_or_links, Iterable):
                raise TypeError("Cannot assign an iterable to a single index")
            self._set_single_item(to_index(index), link_or_links)
        else:
            raise TypeError(f"Invalid index type: {type(index).__name__}")

    def _delete_single_item(self, index: int) -> None:
        """Handles deletion for a single element."""
        if 0 < index < len(self._links) - 1:
            self._links[index - 1].next_ = self._links[index + 1]
        elif index > 0:
            self._links[index - 1].next_ = None
        del self._links[index]

    def _delete_slice_items(self, index: slice, /) -> None:
        start, stop, step = index.indices(len(self._links))
        if start > 0:
            if stop < len(self._links):
                self._links[start - 1].next_ = self._links[stop]
            else:
                self._links[start - 1].next_ = None
        for i in range(start, min(stop, len(self._links) - 1), step):
            if (i + step) < stop:
                self._links[i].next_ = self._links[i + 1]
            else:
                self._links[i].next_ = None
        del self._links[index]

    def _set_single_item(self, index, link: _ChainLink, /) -> None:
        self._link_validator.validate(link)
        self._links[index] = link
        self._set_next__links(index, link)

    def _set_slice_items(
        self, index: slice, links: Iterable[_ChainLink], /
    ) -> None:
        self._link_validator.validate(*links)
        self._links[index] = list(links)
        for i in range(index.start or 0, index.stop or len(self._links) - 1):
            self._set_next__links(i, self._links[i])

    def _set_next__links(self, index: int, value: _ChainLink) -> None:
        if index > 0:
            self._links[index - 1].next_ = value
        if index < len(self._links):
            value.next_ = self._links[index]

    def append(self, value: _ChainLink) -> None:
        self._link_validator.validate(value)
        self._links.append(value)
        self._set_next__links(len(self._links) - 1, value)

    def clear(self) -> None:
        self._links.clear()

    def extend(self, values: Iterable[_ChainLink]) -> None:
        self._link_validator.validate(*values)
        new_links = list(values)
        if not new_links:
            return
        if self._links:
            self._links[-1].next_ = new_links[0]
        for i in range(len(new_links) - 1):
            new_links[i].next_ = new_links[i + 1]
        self._links.extend(new_links)

    def insert(self, index: int, value: _ChainLink) -> None:
        self._link_validator.validate(value)
        self._set_next__links(index, value)
        self._links.insert(index, value)

    def validate_chain(self, *args: Any, **kwargs: Any) -> None:
        if not self._links:
            raise EmptyChainException(self)
        return self._links[0].validate(*args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(base_cls={self.base!r})"

    def __str__(self) -> str:
        return " -> ".join(map(str, self._links))

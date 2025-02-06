from __future__ import annotations

from collections.abc import Generator, Iterable, MutableSequence
from operator import index as to_index
from typing import Any, Generic, SupportsIndex, TypeVar, overload

from domprob.announcements.validation.base_validator import BaseValidator
from domprob.announcements.validation.chain_validation import (
    ABCLinkValidator,
    ABCLinkValidatorContext,
    EmptyChainException,
    LinkValidatorContext,
)

# Typing helper: defines a validator implementing the abstract class
_ChainLink = TypeVar("_ChainLink", bound=BaseValidator)


class ValidationChain(Generic[_ChainLink], MutableSequence[_ChainLink]):
    """A class that represents a chain of validators for validating
    links.

    The `ValidationChain` class manages a collection of validators that
    can sequentially validate links. It provides methods to add,
    insert, and remove validators, as well as to execute validations in
    a structured manner. The chain ensures type consistency and
    supports extensibility.

    Attributes:
        base (type): The expected base type for all links in the chain.

    Args:
        base (type): The base type that all links in the chain must
            conform to.
        *link_validators (ABCLinkValidator): A list of validators in
            the chain.
        validator_context (ABCLinkValidatorContext, optional):
            The context in which the validators are validated.

    Examples:
        >>> from domprob.announcements.validation.base_validator import BaseValidator
        >>> from domprob.announcements.validation.chain import (
        ...     ABCLinkValidatorContext, ValidationChain
        ... )
        >>> class ExampleValidator(ABCLinkValidator):
        ...     def validate(self, link: BaseValidator) -> None:
        ...         pass
        ...
        >>> chain = ValidationChain(BaseValidator)
        >>> chain
        ValidationChain(base='BaseValidator')
    """

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
        """Checks if the validation chain contains any validators.

        Returns:
            bool: `True` if the chain has validators, `False` otherwise.

        Examples:
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>> from domprob.announcements.validation.chain import (
            ...     ABCLinkValidatorContext, ValidationChain
            ... )
            >>> from domprob.announcements.method import BoundAnnouncementMethod
            >>>
            >>> chain = ValidationChain(BaseValidator)
            >>> bool(chain)
            False

            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, link: BaseValidator) -> None:
            ...         pass
            ...
            >>> chain.append(ExampleValidator())
            >>> bool(chain)
            True
        """
        return bool(self._links)

    def __contains__(self, item: object) -> bool:
        """Checks if a specific validator exists in the validation
        chain.

        Args:
            item (object): The item to check for.

        Returns:
            bool: `True` if the validator is in the chain, `False` otherwise.

        Examples:
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>> from domprob.announcements.validation.chain import ValidationChain
            >>> from domprob.announcements.method import BoundAnnouncementMethod
            >>>
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, method: BoundAnnouncementMethod) -> None:
            ...         pass
            ...
            >>> chain = ValidationChain(BaseValidator)
            >>> "" in chain
            False

            >>> validator = ExampleValidator()
            >>> chain.append(validator)
            >>> validator in chain
            True
        """
        if not isinstance(item, self.base):
            return False
        return item in self._links

    def __delitem__(self, index: SupportsIndex | slice, /) -> None:
        """Removes a validator at a specified index from the validation
        chain.

        This method allows the use of the `del` keyword to remove a
        validator from the chain by its position in the list.

        Args:
            index (int): The index of the validator to remove.

        Raises:
            IndexError: If the index is out of range.

        Examples:
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>> from domprob.announcements.validation.chain import ValidationChain
            >>> from domprob.announcements.method import BoundAnnouncementMethod
            >>>
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, method: BoundAnnouncementMethod) -> None:
            ...         pass
            ...
            >>> chain = ValidationChain(BaseValidator)
            >>> validator = ExampleValidator()
            >>> chain.append(validator)
            >>> len(chain)
            1
            >>> del chain[0]
            >>> len(chain)
            0
        """
        if isinstance(index, slice):
            self._delete_slice_items(index)
        elif isinstance(index, int):
            self._delete_single_item(to_index(index))
        else:
            raise TypeError(f"Invalid index type: {type(index).__name__}")

    def __eq__(self, other: Any) -> bool:
        """Compares two validation chains for equality.

        Two validation chains are considered equal if they have the
        same base type and contain the same validators in the same
        order.

        Args:
            other (object): The object to compare with.

        Returns:
            bool: `True` if the chains are equal, `False` otherwise.

        Examples:
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>> from domprob.announcements.validation.chain import ValidationChain
            >>> from domprob.announcements.method import BoundAnnouncementMethod
            >>>
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, method: BoundAnnouncementMethod) -> None:
            ...         pass
            ...
            >>> chain_1 = ValidationChain(BaseValidator)
            >>> chain_2 = ValidationChain(BaseValidator)
            >>> chain_1 == chain_2
            True

            >>> chain_1 == ""
            False

            >>> chain_1.append(ExampleValidator())
            >>> chain_1 == chain_2
            False
        """
        if not isinstance(other, ValidationChain):
            return False
        return self._links == other._links

    @overload
    # need to match the superclasses overloaded signatures
    def __getitem__(self, index: int, /) -> _ChainLink: ...

    @overload
    # need to match the superclasses overloaded signatures
    def __getitem__(self, index: slice, /) -> MutableSequence[_ChainLink]: ...

    def __getitem__(
        self, index: int | slice, /
    ) -> _ChainLink | MutableSequence[_ChainLink]:
        """Retrieves the validator at a specific index in the
        validation chain.

        This method allows the use of indexing to access a validator in
        the chain.

        Args:
            index (int): The index of the validator to retrieve.

        Returns:
            ABCLinkValidator: The validator at the specified index.

        Raises:
            IndexError: If the index is out of range.

        Examples:
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>> from domprob.announcements.validation.chain import ValidationChain
            >>> from domprob.announcements.method import BoundAnnouncementMethod
            >>>
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, method: BoundAnnouncementMethod) -> None:
            ...         pass
            ...
            >>> chain = ValidationChain(BaseValidator)
            >>> chain.append(ExampleValidator())
            >>> chain[0]
            ExampleValidator(next_=None)
        """
        return self._links[index]

    def __iter__(self) -> Generator[_ChainLink, None, None]:
        """Returns an iterator over the validators in the validation
        chain.

        This method allows the validation chain to be iterated over
        directly, returning each validator in sequence.

        Returns:
            Iterator[ABCLinkValidator]: An iterator over the
                validators.

        Examples:
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>> from domprob.announcements.validation.chain import ValidationChain
            >>> from domprob.announcements.method import BoundAnnouncementMethod
            >>>
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, method: BoundAnnouncementMethod) -> None:
            ...         pass
            ...
            >>> chain = ValidationChain(BaseValidator)
            >>> chain.append(ExampleValidator())
            >>> chain.append(ExampleValidator())
            >>>
            >>> for link in chain:
            ...     repr(link)
            ...
            'ExampleValidator(next_=ExampleValidator(next_=None))'
            'ExampleValidator(next_=None)'
        """
        yield from self._links

    def __len__(self) -> int:
        """Returns the number of validators in the validation chain.

        This method allows the use of the `len()` function to determine
        how many validators are in the chain.

        Returns:
            int: The number of validators in the chain.

        Examples:
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>> from domprob.announcements.validation.chain import ValidationChain
            >>> from domprob.announcements.method import BoundAnnouncementMethod
            >>>
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, method: BoundAnnouncementMethod) -> None:
            ...         pass
            ...
            >>> chain = ValidationChain(BaseValidator)
            >>> len(chain)
            0
            >>> chain.append(ExampleValidator())
            >>> len(chain)
            1
        """
        return len(self._links)

    @overload
    # need to match the superclasses overloaded signatures
    def __setitem__(self, index: int, link: _ChainLink, /) -> None: ...

    @overload
    # need to match the superclasses overloaded signatures
    def __setitem__(
        self, index: slice, links: Iterable[_ChainLink], /
    ) -> None: ...

    def __setitem__(
        self,
        index: SupportsIndex | slice,
        link_or_links: _ChainLink | Iterable[_ChainLink],
        /,
    ) -> None:
        """Replaces a validator at the specified index in the
        validation chain.

        This method allows the use of indexing to replace a validator
        at a specific position in the chain.

        Args:
            index (SupportsIndex | slice): The index of the validator
                to replace.
            link_or_links (_ChainLink | Iterable[_ChainLink]): The new
                validator(s) to set at the specified index.

        Raises:
            IndexError: If the index is out of range.
            TypeError: If the provided validator is not an instance of
                `self.base`.

        Examples:
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>> from domprob.announcements.validation.chain import ValidationChain
            >>> from domprob.announcements.method import BoundAnnouncementMethod
            >>>
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, method: BoundAnnouncementMethod) -> None:
            ...         pass
            ...
            >>> chain = ValidationChain(BaseValidator)
            >>> chain.append(ExampleValidator())
            >>>
            >>> chain[0] = ExampleValidator()
        """
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

    def _delete_single_item(self, index: int, /) -> None:
        """Handles deletion for a single element."""
        if index < 0:
            index += len(self._links)  # Turn negative index into actual index
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
        if index < 0:
            index += len(self._links)  # Turn negative index into actual index
        self._links[index] = link
        self._set_next__links(index, link)

    def _set_slice_items(
        self, index: slice, links: Iterable[_ChainLink], /
    ) -> None:
        self._link_validator.validate(*links)
        self._links[index] = list(links)
        for i in range(index.start or 0, index.stop or len(self._links) - 1):
            self._set_next__links(i, self._links[i])

    def _set_next__links(self, index: int, value: _ChainLink, /) -> None:
        # Not the first element
        if index > 0:
            self._links[index - 1].next_ = value
        # Not the only or last element
        if len(self._links) != 0 and index < len(self._links) - 1:
            value.next_ = self._links[index + 1]

    def append(self, value: _ChainLink) -> None:
        """Adds a validator to the end of the validation chain.

        This method allows adding a new validator to the chain,
        ensuring it follows the chain's base type requirements.

        Args:
            value (BaseValidator): The validator to add to the chain.

        Raises:
            TypeError: If the provided validator is not an instance of
                `self.base`.

        Examples:
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>> from domprob.announcements.validation.chain import ValidationChain
            >>> from domprob.announcements.method import BoundAnnouncementMethod
            >>>
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, method: BoundAnnouncementMethod) -> None:
            ...         pass
            ...
            >>> chain = ValidationChain(BaseValidator)
            >>> chain.append(ExampleValidator())
        """
        self._link_validator.validate(value)
        self._links.append(value)
        self._set_next__links(len(self._links) - 1, value)

    def clear(self) -> None:
        """Removes all validators from the validation chain.

        Examples:
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>> from domprob.announcements.validation.chain import ValidationChain
            >>> from domprob.announcements.method import BoundAnnouncementMethod
            >>>
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, method: BoundAnnouncementMethod) -> None:
            ...         pass
            ...
            >>> chain = ValidationChain(BaseValidator)
            >>> chain.append(ExampleValidator())
            >>> chain.append(ExampleValidator())
            >>> len(chain)
            2
            >>> chain.clear()
            >>> len(chain)
            0
        """
        self._links.clear()

    def extend(self, values: Iterable[_ChainLink]) -> None:
        """Adds multiple validators to the end of the validation chain.

        This method appends a list of validators to the chain. It
        ensures that each validator conforms to the chain's base type
        requirements.

        Args:
            values (Iterable[BaseValidator]): An iterable of validators
                to add to the chain.

        Raises:
            TypeError: If any of the provided validators are not
                instances of `self.base`.

        Examples:
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>> from domprob.announcements.validation.chain import ValidationChain
            >>> from domprob.announcements.method import BoundAnnouncementMethod
            >>>
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, method: BoundAnnouncementMethod) -> None:
            ...         pass
            ...
            >>> chain = ValidationChain(BaseValidator)
            >>> chain.extend([ExampleValidator(), ExampleValidator()])
            >>> len(chain)
            2
        """
        new_links = list(values)
        self._link_validator.validate(*new_links)
        if not new_links:
            return
        if self._links:
            self._links[-1].next_ = new_links[0]
        for i in range(len(new_links) - 1):
            new_links[i].next_ = new_links[i + 1]
        self._links.extend(new_links)

    def insert(self, index: int, value: _ChainLink) -> None:
        """Inserts a validator at the specified index in the validation
        chain.

        This method adds a new validator at a specific position in the
        chain, shifting subsequent validators to the right.

        Args:
            index (int): The position to insert the validator.
            value (BaseValidator): The validator to insert.

        Raises:
            TypeError: If the provided validator is not an instance of
                `self.base`.

        Examples:
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>> from domprob.announcements.validation.chain import ValidationChain
            >>> from domprob.announcements.method import BoundAnnouncementMethod
            >>>
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, method: BoundAnnouncementMethod) -> None:
            ...         pass
            ...
            >>> chain = ValidationChain(BaseValidator)
            >>> chain.insert(0, ExampleValidator())
            >>> len(chain)
            1
        """
        self._link_validator.validate(value)
        # Turn negative index into actual index
        if index < 0:
            index += len(self._links)
        self._links.insert(index, value)
        self._set_next__links(index, value)

    def validate_chain(self, *args: Any, **kwargs: Any) -> None:
        """Validates the entire chain to ensure it meets the base type
        requirements.

        This method checks that all validators in the chain are valid
        and comply with the chain's expected rules. It raises an
        exception if any validator is invalid.

        Examples:
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>> from domprob.announcements.validation.chain import ValidationChain
            >>> from domprob.announcements.method import BoundAnnouncementMethod
            >>>
            >>> chain = ValidationChain(BaseValidator)
            >>> try:
            ...     chain.validate_chain()
            ... except EmptyChainException as e:
            ...     print(e)
            ...
            Nothing to validate, no links added to chain 'ValidationChain(base='BaseValidator')'
        """
        if not self._links:
            raise EmptyChainException(self)
        return self._links[0].validate(*args, **kwargs)

    def __repr__(self) -> str:
        """Returns a string representation of the `ValidationChain`
        instance.

        Returns:
            str: A string representation of the `ValidationChain`.

        Examples:
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>> from domprob.announcements.validation.chain import ValidationChain
            >>> from domprob.announcements.method import BoundAnnouncementMethod
            >>>
            >>> chain = ValidationChain(BaseValidator)
            >>> repr(chain)
            "ValidationChain(base='BaseValidator')"
        """
        return f"{self.__class__.__name__}(base={self.base.__name__!r})"

    def __str__(self) -> str:
        """Returns a human-readable string representation of the
        `ValidationChain`.

        Returns:
            str: A user-friendly string representation of the
                `ValidationChain`.

        Examples:
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>> from domprob.announcements.validation.chain import ValidationChain
            >>> from domprob.announcements.method import BoundAnnouncementMethod
            >>>
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, method: BoundAnnouncementMethod) -> None:
            ...         pass
            ...
            >>> chain = ValidationChain(BaseValidator)
            >>> chain.append(ExampleValidator())
            >>> chain.append(ExampleValidator())
            >>> str(chain)
            'ExampleValidator -> ExampleValidator'
        """
        return " -> ".join(map(str, self._links))

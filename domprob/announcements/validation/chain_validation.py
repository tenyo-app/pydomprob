from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, TypeVar

from domprob.announcements.exceptions import AnnouncementException
from domprob.announcements.validation.base_validator import BaseValidator

if TYPE_CHECKING:
    from domprob.announcements.validation.chain import (  # pragma: no cover
        ValidationChain,
    )

# Typing helper: defines a validator implementing the abstract class
_ChainLink = TypeVar("_ChainLink", bound=BaseValidator)


class ValidationChainException(AnnouncementException):
    """Base exception class for errors related to validation chains.

    This exception serves as the root for all validation chain-related
    errors, such as issues with chain construction, execution, or
    invalid links. It is designed to be extended by more specific
    exceptions within the validation framework.
    """


class InvalidLinkException(ValidationChainException):
    """Exception raised when an invalid link is added to a validation
    chain.

    This exception is used to indicate that a link in the validation
    chain does not meet the required criteria or fails validation. It
    provides detailed information about the invalid link and the
    expected type.

    Attributes:
        link (Any): The invalid link that caused the exception.
        expected_type (type[Any]): The expected type for valid links in
            the chain.

    Args:
        link (Any): The link object that is invalid.
        expected_type (type[Any]): The expected type for links in the
            validation chain.

    Examples:
        >>> from domprob.exceptions import InvalidLinkException
        >>>
        >>> def raise_invalid_link():
        ...     raise InvalidLinkException("InvalidLink", expected_type=int)
        ...
        >>> try:
        ...     raise_invalid_link()
        ... except InvalidLinkException as e:
        ...     print(str(e))
        Invalid link of type 'str', expected type 'int'
    """

    def __init__(self, link: Any, expected_type: type[Any]) -> None:
        self.link = link
        self.expected_type = expected_type
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        """Constructs a detailed error message for the exception.

        This property dynamically generates a human-readable string
        that describes the invalid link and the expected type.

        Returns:
            str: A string describing the invalid link and its expected
                type.

        Examples:
            >>> exc = InvalidLinkException("InvalidLink", expected_type=int)
            >>> exc.msg
            "Invalid link of type 'str', expected type 'int'"
        """
        l_name = type(self.link).__name__
        e_name = self.expected_type.__name__
        return f"Invalid link of type '{l_name}', expected type '{e_name}'"


class EmptyChainException(ValidationChainException):
    """Exception raised when a validation chain is empty.

    This exception indicates that no validators have been added to a
    validation chain, which prevents the chain from performing any
    meaningful validation.

    Args:
        chain (ValidationChain): The empty validation chain.

    Attributes:
        chain (ValidationChain): The empty validation chain.

    Examples:
        >>> from domprob.exceptions import EmptyChainException
        >>> from domprob.announcements.validation.base_validator import BaseValidator
        >>> from domprob.announcements.validation.chain import ValidationChain
        >>>
        >>> try:
        ...     raise EmptyChainException(ValidationChain(BaseValidator))
        ... except EmptyChainException as e:
        ...     print(e)
        ...
        Nothing to validate, no links added to chain 'ValidationChain(base='BaseValidator')'
    """

    def __init__(self, chain: ValidationChain) -> None:
        self.chain = chain
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        """Returns the error message associated with the exception.

        Returns:
            str: The error message describing the empty validation
                chain issue.

        Examples:
            >>> from domprob.exceptions import EmptyChainException
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>> from domprob.announcements.validation.chain import ValidationChain
            >>>
            >>> exc = EmptyChainException(ValidationChain(BaseValidator))
            >>> exc.msg
            "Nothing to validate, no links added to chain 'ValidationChain(base='BaseValidator')'"
        """
        return f"Nothing to validate, no links added to chain '{self.chain!r}'"


class LinkExistsException(ValidationChainException):
    # pylint: disable=line-too-long
    """Exception raised when a duplicate link is added to a validation
    chain.

    This exception is used to indicate that the specified link already
    exists in the validation chain and duplicates are not allowed. It
    provides details about the duplicate link and the chain where the
    conflict occurred.

    Args:
        link (Any): The duplicate link that caused the exception.
        chain (ValidationChain): The validation chain where the
            duplicate was found.

    Attributes:
        link (Any): The duplicate link.
        chain (ValidationChain): The chain where the duplicate was
            detected.

    Examples:
        >>> from domprob.exceptions import LinkExistsException
        >>> from domprob.announcements.validation.base_validator import BaseValidator
        >>> from domprob.announcements.validation.chain import ValidationChain
        >>>
        >>> try:
        ...     raise LinkExistsException("DuplicateLink", chain=ValidationChain(BaseValidator))  # type: ignore
        ... except LinkExistsException as e:
        ...     print(e)
        ...
        Link ''DuplicateLink'' already exists in chain 'ValidationChain(base='BaseValidator')'
    """

    def __init__(self, link: _ChainLink, chain: ValidationChain) -> None:
        self.link = link
        self.chain = chain
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        """Constructs a detailed error message indicating a duplicate
        link in the validation chain.

        Returns:
            str: A message indicating the duplicate link and the
                affected chain.

        Examples:
            >>> from domprob.exceptions import LinkExistsException
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>> from domprob.announcements.validation.chain import ValidationChain
            >>>
            >>> chain = ValidationChain(base=BaseValidator)
            >>> exc = LinkExistsException("DuplicateLink", chain)  # type: ignore
            >>> exc.msg
            "Link ''DuplicateLink'' already exists in chain 'ValidationChain(base='BaseValidator')'"
        """
        return f"Link '{self.link!r}' already exists in chain '{self.chain!r}'"


# pylint: disable=too-few-public-methods
class ABCLinkValidator(ABC):
    """Abstract base class for validators in a validation chain.

    This class defines the structure for implementing validators that
    perform specific checks on links within a validation chain.

    Attributes:
        chain (ValidationChain): The validation chain associated with
            this validator. It provides context for the validation
            process.

    Args:
        chain (ValidationChain): The validation chain to associate with
            this validator.

    Examples:
        >>> from domprob.announcements.validation.chain import ABCLinkValidator
        >>> from domprob.announcements.validation.base_validator import BaseValidator
        >>>
        >>> class ExampleValidator(ABCLinkValidator):
        ...     def validate(self, link: BaseValidator) -> None:
        ...         pass
        ...
    """

    def __init__(self, chain: ValidationChain) -> None:
        self.chain = chain

    @abstractmethod
    def validate(self, link: _ChainLink) -> None:
        """Validates a single link in the validation chain.

        This abstract method must be implemented by subclasses to
        define specific validation logic.

        Args:
            link (_ChainLink): The link to validate.

        Raises:
            NotImplementedError: If the subclass does not implement
                this method.
        """
        raise NotImplementedError  # pragma: no cover

    def __repr__(self) -> str:
        """Returns a string representation of the validator.

        Returns:
            str: A string representation of the validator, including
                its class name and the validation chain it belongs to.

        Examples:
            >>> from domprob.announcements.validation.chain import ABCLinkValidator
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>>
            >>> class ExampleValidator(ABCLinkValidator):
            ...     def validate(self, link: BaseValidator) -> None:
            ...         pass
            ...
            >>> from domprob.announcements.validation.chain import ValidationChain
            >>>
            >>> validator = ExampleValidator(ValidationChain(BaseValidator))
            >>> repr(validator)
            "ExampleValidator(ValidationChain(base='BaseValidator'))"
        """
        return f"{self.__class__.__name__}({self.chain!r})"


class LinkTypeValidator(ABCLinkValidator):
    """Validator to ensure that links in the validation chain are of
    the expected type.

    This validator checks whether each link added to the validation
    chain is an instance of the chain's base type. If a link does not
    match the expected type, it raises an `InvalidLinkException`. This
    ensures type safety and consistency within the chain.

    Attributes:
        chain (ValidationChain): The validation chain this validator is
            associated with.

    Examples:
        >>> from domprob.announcements.validation.chain_validation import LinkTypeValidator
        >>> from domprob.announcements.validation.chain import ValidationChain
        >>> from domprob.announcements.validation.base_validator import BaseValidator
        >>>
        >>> validator = LinkTypeValidator(ValidationChain(BaseValidator))
        >>>
        >>> try:
        ...     validator.validate(123)  # type: ignore
        ... except InvalidLinkException as e:
        ...     print(e)
        ...
        Invalid link of type 'int', expected type 'BaseValidator'
    """

    def validate(self, link: _ChainLink) -> None:
        """Validates that the provided link is of the expected type.

        This method ensures that the given link is an instance of the
        chain's base type. If the link is not of the expected type, it
        raises an `InvalidLinkException`.

        Args:
            link (_ChainLink): The link to validate.

        Raises:
            InvalidLinkException: If the link is not of the expected type.

        Examples:
            >>> from domprob.announcements.validation.chain_validation import LinkTypeValidator
            >>> from domprob.announcements.validation.chain import ValidationChain
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>>
            >>> validator = LinkTypeValidator(ValidationChain(BaseValidator))
            >>>
            >>> try:
            ...     validator.validate(123)  # type: ignore
            ... except InvalidLinkException as e:
            ...     print(e)
            ...
            Invalid link of type 'int', expected type 'BaseValidator'
        """
        if not isinstance(link, self.chain.base):
            raise InvalidLinkException(link, self.chain.base)


class UniqueLinkValidator(ABCLinkValidator):
    # pylint: disable=line-too-long
    """Validator to ensure that links in the validation chain are
    unique.

    This validator checks whether a link already exists in the
    validation chain. If a duplicate link is detected, it raises a
    `LinkExistsException`. This ensures that all links in the chain are
    unique.

    Attributes:
        chain (ValidationChain): The validation chain this validator is
            associated with.

    Examples:
        >>> from domprob.announcements.validation.chain_validation import LinkTypeValidator
        >>> from domprob.announcements.validation.chain import ValidationChain
        >>> from domprob.announcements.validation.base_validator import BaseValidator
        >>>
        >>> chain = ValidationChain(BaseValidator)
        >>> validator = UniqueLinkValidator(chain)
        >>>
        >>> class ExampleValidator(BaseValidator):
        ...     def validate(self, link: BaseValidator) -> None:
        ...         pass
        ...
        >>> example_validator = ExampleValidator()
        >>> chain.append(example_validator)
        >>>
        >>> try:
        ...     validator.validate(example_validator)
        ... except LinkExistsException as e:
        ...     print(e)
        ...
        Link 'ExampleValidator(next_=None)' already exists in chain 'ValidationChain(base='BaseValidator')'
    """

    def validate(self, link: _ChainLink) -> None:
        # noinspection PyShadowingNames
        """Validates that the provided link does not already exist in
        the validation chain.

        This method checks whether the given link is already present in
        the validation chain. If the link is a duplicate, it raises a
        `LinkExistsException`. This ensures that all links within the
        chain are unique.

        Args:
            link (_ChainLink): The link to validate.

        Raises:
            LinkExistsException: If the link already exists in the validation chain.

        Examples:
            >>> from domprob.announcements.validation.chain_validation import LinkTypeValidator
            >>> from domprob.announcements.validation.chain import ValidationChain
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>>
            >>> chain = ValidationChain(BaseValidator)
            >>> validator = UniqueLinkValidator(chain)
            >>>
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, link: BaseValidator) -> None:
            ...         pass
            ...
            >>> example_validator = ExampleValidator()
            >>> chain.append(example_validator)
            >>>
            >>> try:
            ...     validator.validate(example_validator)
            ... except LinkExistsException as e:
            ...     print(e)
            ...
            Link 'ExampleValidator(next_=None)' already exists in chain 'ValidationChain(base='BaseValidator')'
        """
        if link in self.chain:
            raise LinkExistsException(link, self.chain)


class ABCLinkValidatorContext(ABC):
    """Abstract base class for context-aware link validators in a
    validation chain.

    This class provides an interface for validators that need
    additional context about the validation chain during the validation
    process. It enforces the implementation of the `validate` method,
    allowing subclasses to perform more sophisticated validations that
    depend on the state of the chain.

    Attributes:
        chain (ValidationChain): The validation chain associated with
            this validator. It provides context for the validation
            process.

    Args:
        chain (ValidationChain): The validation chain to associate with
            this context-aware validator.

    Examples:
        >>> from domprob.announcements.validation.chain import (
        ...     ABCLinkValidatorContext, ValidationChain
        ... )
        >>> from domprob.announcements.validation.base_validator import BaseValidator
        >>>
        >>> class ExampleValidator(BaseValidator):
        ...     def validate(self, link: BaseValidator) -> None:
        ...         pass
        ...
        >>>
        >>> class ExampleContext(ABCLinkValidatorContext):
        ...     def add_validators(self, *validators: type[BaseValidator]) -> None:
        ...         pass
        ...
        ...     def validate(self, link: BaseValidator) -> None:
        ...         pass
        ...
        >>> chain = ValidationChain(BaseValidator)
        >>> validator_context = ExampleContext(chain)
        >>> validator_context.validate(ExampleValidator())
    """

    def __init__(
        self, chain: ValidationChain, *validators: type[ABCLinkValidator]
    ) -> None:
        self.chain = chain
        self.validators: list[type[ABCLinkValidator]] = []
        self.add_validators(*validators)

    @abstractmethod
    def add_validators(self, *validators: type[ABCLinkValidator]) -> None:
        # noinspection PyShadowingNames
        """Adds one or more validators to the validation chain.

        This abstract method is designed to allow additional validators
        to be dynamically added to the validation chain during runtime.
        Each validator is appended to the chain, enabling
        customisation and extensibility of the validation process.

        Args:
            *validators (ABCLinkValidator): One or more validator
                instances to add to the validation chain.

        Examples:
            >>> from domprob.announcements.validation.chain import (
            ...     ABCLinkValidatorContext, ValidationChain
            ... )
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>>
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, link: BaseValidator) -> None:
            ...         pass
            ...
            >>> class ExampleContext(ABCLinkValidatorContext):
            ...     def add_validators(self, *validators: type[BaseValidator]) -> None:
            ...         pass
            ...
            ...     def validate(self, link: BaseValidator) -> None:
            ...         pass
            ...
            >>> chain = ValidationChain(ExampleValidator)
            >>> context = ExampleContext(chain)
            >>> context.add_validators(ExampleValidator, ExampleValidator)
        """
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def validate(self, link: _ChainLink) -> None:
        # noinspection PyShadowingNames
        """Abstract method to validate a link in the chain using
        additional context.

        This method must be implemented by subclasses to provide logic
        for validating a link with additional contextual information.
        This allows the validator to account for dynamic rules or
        states during validation.

        Args:
            link (_ChainLink): The link to validate.

        Raises:
            NotImplementedError: If a subclass does not implement this
                method.

        Examples:
            >>> from domprob.announcements.validation.chain import (
            ...     ABCLinkValidatorContext, ValidationChain
            ... )
            >>>
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, link: BaseValidator) -> None:
            ...         pass
            ...
            >>>
            >>> class ExampleContext(ABCLinkValidatorContext):
            ...     def add_validators(self, *validators: type[BaseValidator]) -> None:
            ...         pass
            ...
            ...     def validate(self, link: BaseValidator) -> None:
            ...         pass
            ...
            >>> chain = ValidationChain(ExampleValidator)
            >>> validator_context = ExampleContext(chain)
            >>> validator_context.validate(ExampleValidator())
        """
        raise NotImplementedError  # pragma: no cover

    def __repr__(self) -> str:
        """Returns a string representation of the context-aware
        validator.

        Returns:
            str: A string representation of the validator, showing the
                class name and the validation chain it is associated
                with.

        Examples:
            >>> from domprob.announcements.validation.chain import (
            ...     ABCLinkValidatorContext,
            ...     BaseValidator,
            ...     ValidationChain
            ... )
            >>>
            >>> class ExampleValidator(BaseValidator):
            ...     def validate(self, link: BaseValidator) -> None:
            ...         pass
            ...
            >>> class ExampleContext(ABCLinkValidatorContext):
            ...     def add_validators(self, *validators: type[BaseValidator]) -> None:
            ...         pass
            ...
            ...     def validate(self, link: BaseValidator) -> None:
            ...         pass
            ...
            >>> chain = ValidationChain(ExampleValidator)
            >>> context = ExampleContext(chain)
            >>> repr(context)
            "ExampleContext(chain=ValidationChain(base='ExampleValidator'))"
        """
        return f"{self.__class__.__name__}(chain={self.chain!r})"


class LinkValidatorContext(ABCLinkValidatorContext):
    """Concrete implementation of a context-aware link validator.

    The `LinkValidatorContext` class extends `ABCLinkValidatorContext`
    to provide validation logic for links in a chain, utilising
    additional contextual information. It allows flexible and dynamic
    validation of links, depending on the state of the chain or
    external conditions.

    Attributes:
        chain (ValidationChain): The validation chain associated with
            this context-aware validator.

    Args:
        chain (ValidationChain): The validation chain to associate with
            the validator.

    Examples:
        >>> from domprob.announcements.validation.chain import (
        ...     ABCLinkValidatorContext, ValidationChain
        ... )
        >>> from domprob.announcements.validation.chain_validation import InvalidLinkException
        >>>
        >>> class ExampleLink:
        ...     pass
        ...
        >>> chain = ValidationChain(BaseValidator)
        >>> validator_context = LinkValidatorContext(chain)
        >>> try:
        ...     validator_context.validate("invalid_link")  # type: ignore
        ... except InvalidLinkException as e:
        ...     print(e)
        Invalid link of type 'str', expected type 'BaseValidator'
    """

    DEFAULT_VALIDATORS: tuple[type[ABCLinkValidator], ...] = (
        LinkTypeValidator,
        UniqueLinkValidator,
    )

    def __init__(
        self, chain: ValidationChain, *validators: type[ABCLinkValidator]
    ) -> None:
        super().__init__(chain, *self.DEFAULT_VALIDATORS, *validators)

    def add_validators(self, *validators: type[ABCLinkValidator]) -> None:
        """Adds one or more validators to the validation chain.

        This method allows the dynamic addition of validators to the
        validation chain at runtime. Each provided validator is
        appended to the chain, enabling custom validation logic and
        extensibility.

        Args:
            *validators (ABCLinkValidator): One or more validator
                instances to add to the validation chain.

        Examples:
            >>> from domprob.announcements.validation.chain import (
            ...     ABCLinkValidatorContext, ValidationChain
            ... )
            >>> from domprob.announcements.validation.base_validator import BaseValidator
            >>>
            >>> class ExampleValidator(ABCLinkValidator):
            ...     def validate(self, link: BaseValidator) -> None:
            ...         pass
            ...
            >>> chain = ValidationChain(BaseValidator)
            >>> context = LinkValidatorContext(chain)
            >>> context.add_validators(ExampleValidator, ExampleValidator)
        """
        self.validators.extend(validators)

    def validate(self, *links: _ChainLink) -> None:
        """Validates a link in the chain.

        This method performs validation on the given links using the
        validators in the validation chain. It ensures that the link
        meets all the criteria enforced by the chain's validators.

        Args:
            *links (_ChainLink): The links to validate.

        Raises:
            Any: Exceptions raised by the individual validators in the
                chain if the link does not meet the required criteria.

        Examples:
            >>> from domprob.announcements.validation.chain import (
            ...     ABCLinkValidatorContext, ValidationChain
            ... )
            >>> from domprob.announcements.validation.chain_validation import InvalidLinkException
            >>>
            >>> class ExampleLink:
            ...     pass
            ...
            >>> chain = ValidationChain(BaseValidator)
            >>> validator_context = LinkValidatorContext(chain)
            >>> try:
            ...     validator_context.validate("invalid_link")  # type: ignore
            ... except InvalidLinkException as e:
            ...     print(e)
            Invalid link of type 'str', expected type 'BaseValidator'
        """
        for validator in self.validators:
            for link in links:
                validator(self.chain).validate(link)

    def __repr__(self) -> str:
        """Returns a string representation of the
        `LinkValidatorContext`.

        Returns:
            str: A string representation of the context, including its
                class name and the associated validation chain.

        Examples:
            >>> from domprob.announcements.validation.chain import (
            ...     ABCLinkValidatorContext, ValidationChain
            ... )
            >>>
            >>> class ExampleLink:
            ...     pass
            ...
            >>> chain = ValidationChain(BaseValidator)
            >>> validator_context = LinkValidatorContext(chain)
            >>> repr(validator_context)
            "LinkValidatorContext(ValidationChain(base='BaseValidator'))"
        """
        return f"{self.__class__.__name__}({self.chain!r})"

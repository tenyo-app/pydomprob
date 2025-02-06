from __future__ import annotations

from typing import TYPE_CHECKING

from domprob.announcements.validation.base_validator import BaseValidator
from domprob.announcements.validation.chain import ValidationChain
from domprob.announcements.validation.validators import (
    InstrumentParamExistsValidator,
    InstrumentTypeValidator,
    SupportedInstrumentsExistValidator,
)

if TYPE_CHECKING:
    from domprob.announcements.method import (  # pragma: no cover
        BoundAnnouncementMethod,
    )


class AnnouncementValidationOrchestrator:
    # pylint: disable=line-too-long
    """Orchestrates the validation of `BoundAnnouncementMethod`
    instances using a chain of validators.

    The orchestrator is initialised with a `ValidationChain`, which can
    either be customised or use the default set of validators.
    Validators are applied sequentially to ensure that the
    `BoundAnnouncementMethod` adheres to defined rules and constraints.

    Attributes:
        DEFAULT_VALIDATORS (tuple[type[BaseValidator], ...]):
            A tuple of default validator classes used to initialise the
            chain.
        _chain (ValidationChain):
            The validation chain that manages the sequence of
            validators.

    Args:
        chain (ValidationChain | None, optional):
            A custom validation chain. If not provided, a default chain
            is created with `DEFAULT_VALIDATORS`.

    Examples:
        >>> from domprob.announcements.validation.orchestrator import AnnouncementValidationOrchestrator
        >>> from domprob.announcements.method import AnnouncementMethod
        >>>
        >>> class SomeInstrument:
        ...     pass
        ...
        >>> class Example:
        ...     def method(self, instrument: SomeInstrument) -> None:
        ...         pass
        ...
        >>> method = AnnouncementMethod(Example.method)
        >>> method.supp_instrums.record(SomeInstrument, required=True)
        Instruments(metadata=AnnouncementMetadata(method=<function Example.method at 0x...>))
        >>>
        >>> bound_method = method.bind(Example(), SomeInstrument())
        >>>
        >>> orchestrator = AnnouncementValidationOrchestrator()
        >>> orchestrator.validate(bound_method)
    """

    DEFAULT_VALIDATORS: tuple[type[BaseValidator], ...] = (
        SupportedInstrumentsExistValidator,
        InstrumentParamExistsValidator,
        InstrumentTypeValidator,
    )

    def __init__(self, chain: ValidationChain | None = None):
        self._chain = chain or ValidationChain(BaseValidator)
        self.register(*self.DEFAULT_VALIDATORS)

    def register(
        self, *validators: type[BaseValidator]
    ) -> AnnouncementValidationOrchestrator:
        # pylint: disable=line-too-long
        """Registers additional validators to the validation chain.

        Validators are appended to the existing chain, and their
        instances are created dynamically.

        Args:
            *validators (type[BaseValidator]): Validator classes to be
                added to the chain.

        Examples:
            >>> from domprob.announcements.validation.orchestrator import AnnouncementValidationOrchestrator
            >>> from domprob.announcements.validation.validators import InstrumentTypeValidator
            >>>
            >>> orchestrator = AnnouncementValidationOrchestrator()
            >>> orchestrator.register(InstrumentTypeValidator)
            AnnouncementValidationOrchestrator(ValidationChain(base='BaseValidator'))
        """
        self._chain.extend((v() for v in validators))
        return self

    def validate(self, method: BoundAnnouncementMethod):
        # pylint: disable=line-too-long
        """Executes the validation chain on a `BoundAnnouncementMethod`
        instance.

        This method ensures that all registered validators are applied
        sequentially to the method.

        Args:
            method (BoundAnnouncementMethod): The method instance to
                validate.

        Raises:
            ValidatorException: If any of the validators in the chain
                fails.

        Examples:
            >>> from domprob.announcements.validation.orchestrator import AnnouncementValidationOrchestrator
            >>> from domprob.announcements.method import AnnouncementMethod
            >>>
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> class Example:
            ...     def method(self, instrument: SomeInstrument) -> None:
            ...         pass
            ...
            >>> meth = AnnouncementMethod(Example.method)
            >>> bound_meth = meth.bind(Example(), SomeInstrument())
            >>> bound_meth.supp_instrums.record(SomeInstrument, required=True)
            Instruments(metadata=AnnouncementMetadata(method=<function Example.method at 0x...>))
            >>>
            >>> orchestrator = AnnouncementValidationOrchestrator()
            >>> orchestrator.validate(bound_meth)
        """
        self._chain.validate_chain(method)

    def __repr__(self) -> str:
        """Returns a string representation of the orchestrator.

        The representation includes the class name and the associated
        validation chain.

        Returns:
            str: A string representation of the orchestrator.

        Examples:
            >>> orchestrator = AnnouncementValidationOrchestrator()
            >>> repr(orchestrator)
            "AnnouncementValidationOrchestrator(ValidationChain(base='BaseValidator'))"
        """
        return f"{self.__class__.__name__}({self._chain!r})"

from __future__ import annotations

from typing import TYPE_CHECKING

from domprob.sensors.validate.base_val import BaseValidator
from domprob.sensors.validate.chain import ValidationChain
from domprob.sensors.validate.vals import (
    InstrumentParamExistsValidator,
    InstrumentTypeValidator,
    SupportedInstrumentsExistValidator,
)

if TYPE_CHECKING:
    from domprob.sensors.meth import (  # pragma: no cover
        BoundSensorMethod,
    )


class SensorValidationOrchestrator:
    # pylint: disable=line-too-long
    """Orchestrates validation of `BoundSensorMethod` instances using a
    chain of validators.

    The orchestrator is initialised with a `ValidationChain`, which can
    either be customised or use the default set of validators.
    Validators are applied sequentially to ensure that the
    `BoundSensorMethod` adheres to defined rules and constraints.

    Attributes:
        DEFAULT_VALIDATORS (tuple[type[BaseValidator], ...]):
            A tuple of default validator classes used to initialise the
            chain.
        _chain (ValidationChain):
            The validate chain that manages the sequence of
            validators.

    Args:
        chain (ValidationChain | None, optional):
            A custom validate chain. If not provided, a default chain
            is created with `DEFAULT_VALIDATORS`.

    Examples:
        >>> from domprob.sensors.validate.orch import SensorValidationOrchestrator
        >>> from domprob.sensors.meth import SensorMethod
        >>>
        >>> class SomeInstrument:
        ...     pass
        ...
        >>> class Example:
        ...     def method(self, instrument: SomeInstrument) -> None:
        ...         pass
        ...
        >>> method = SensorMethod(Example.method)
        >>> method.supp_instrums.record(SomeInstrument, required=True)
        Instruments(metadata=SensorMetadata(method=<function Example.method at 0x...>))
        >>>
        >>> bound_method = method.bind(Example(), SomeInstrument())
        >>>
        >>> orchestrator = SensorValidationOrchestrator()
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
    ) -> SensorValidationOrchestrator:
        # pylint: disable=line-too-long
        """Registers additional validators to the validate chain.

        Validators are appended to the existing chain, and their
        instances are created dynamically.

        Args:
            *validators (type[BaseValidator]): Validator classes to be
                added to the chain.

        Examples:
            >>> from domprob.sensors.validate.orch import SensorValidationOrchestrator
            >>> from domprob.sensors.validate.vals import InstrumentTypeValidator
            >>>
            >>> orchestrator = SensorValidationOrchestrator()
            >>> orchestrator.register(InstrumentTypeValidator)
            SensorValidationOrchestrator(ValidationChain(base='BaseValidator'))
        """
        self._chain.extend((v() for v in validators))
        return self

    def validate(self, method: BoundSensorMethod):
        # pylint: disable=line-too-long
        """Executes the validate chain on a `BoundSensorMethod`
        instance.

        This method ensures that all registered validators are applied
        sequentially to the method.

        Args:
            method (BoundSensorMethod): The method instance to
                validate.

        Raises:
            ValidatorException: If any of the validators in the chain
                fails.

        Examples:
            >>> from domprob.sensors.validate.orch import SensorValidationOrchestrator
            >>> from domprob.sensors.meth import SensorMethod
            >>>
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> class Example:
            ...     def method(self, instrument: SomeInstrument) -> None:
            ...         pass
            ...
            >>> meth = SensorMethod(Example.method)
            >>> bound_meth = meth.bind(Example(), SomeInstrument())
            >>> bound_meth.supp_instrums.record(SomeInstrument, required=True)
            Instruments(metadata=SensorMetadata(method=<function Example.method at 0x...>))
            >>>
            >>> orchestrator = SensorValidationOrchestrator()
            >>> orchestrator.validate(bound_meth)
        """
        self._chain.validate_chain(method)

    def __repr__(self) -> str:
        """Returns a string representation of the orchestrator.

        The representation includes the class name and the associated
        validate chain.

        Returns:
            str: A string representation of the orchestrator.

        Examples:
            >>> orchestrator = SensorValidationOrchestrator()
            >>> repr(orchestrator)
            "SensorValidationOrchestrator(ValidationChain(base='BaseValidator'))"
        """
        return f"{self.__class__.__name__}({self._chain!r})"

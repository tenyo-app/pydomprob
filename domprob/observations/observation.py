from collections.abc import Iterable
from typing import Any, ParamSpec, Protocol, TypeVar, runtime_checkable

from domprob.sensors.meth import SensorMethod

# Typing helpers: defines an @sensors method signature
_P = ParamSpec("_P")
_R_co = TypeVar("_R_co", bound=Any, covariant=True)


# pylint: disable=too-few-public-methods
@runtime_checkable
class ObservationProtocol(Protocol):
    """Protocol defining the structure of domain observations that
    provide sensors.

    Classes implementing this protocol must define a `@classmethod`
    named `sensors` that returns a `Generator` of
    `SensorMethod` instances.

    This protocol is `@runtime_checkable`, meaning
    `isinstance(obj, ObservationProtocol)` can be used to verify
    implementation at runtime.

    Type Parameters:
        _P (ParamSpec): Represents the parameters accepted by the
            sensors' method.
        _R_co (TypeVar): Represents the return type of the sensors'
            method.

    Example:
        >>> from domprob.sensors.meth import SensorMethod
        >>> from domprob.observations.observation import ObservationProtocol
        >>>
        >>> class ConcreteObservation:
        ...     @classmethod
        ...     def sensors(cls) -> Iterable[SensorMethod]:
        ...         yield SensorMethod(lambda x: x)
        ...
        >>> assert isinstance(ConcreteObservation, ObservationProtocol)
    """

    @classmethod
    def sensors(cls) -> Iterable[SensorMethod]:
        """Retrieve all sensors methods defined in the class.

        Returns:
            Generator[_SensorSig, None, None]: A generator yielding
                `SensorMethod` instances.
        """

from typing import Any, Protocol, runtime_checkable

from domprob.base_exc import DomprobException
from domprob.observations.observation import ObservationProtocol


@runtime_checkable
class ConsumerProtocol(Protocol):
    """Protocol defining the structure for dispatchers handling domain
    observations.

    Classes implementing this protocol must define:

    - `dispatch()`: Processes an `ObservationProtocol` and returns a
      result.
    - `__repr__()`: Provides a string representation of the dispatcher.

    This protocol is `@runtime_checkable`, meaning
    `isinstance(dispatcher, DispatcherProtocol)` can be used to verify
    conformance at runtime.

    Example:
        >>> from domprob.dispatchers.dispatcher import DispatcherProtocol
        >>> from domprob.observations.observation import ObservationProtocol
        >>>
        >>> class ConcreteDispatcher:
        ...     @staticmethod
        ...     def dispatch(self, observation: ObservationProtocol) -> str:
        ...         return "Processed observation"
        ...
        ...     def __repr__(self) -> str:
        ...         return "ConcreteDispatcher()"
        ...
        >>> dispatcher = ConcreteDispatcher()
        >>> assert isinstance(dispatcher, DispatcherProtocol)
    """

    def __eq__(self, other: Any) -> bool: ...
    def __hash__(self) -> int: ...
    def consume(self, observation: ObservationProtocol) -> None:
        """Consume an observation and handle execution.

        Args:
            observation (`ObservationProtocol[_P, _R]`): The
                observation to process.
        """


class ConsumerException(DomprobException):
    """Base exception for errors occurring within consumers.

    This exception is raised when an error occurs while processing
    observations within a consumer.

    It inherits from `DomprobException`, allowing it to be caught
    alongside other domain-specific exceptions.
    """

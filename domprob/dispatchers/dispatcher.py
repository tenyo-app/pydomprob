from typing import (
    TypeVar,
    Any,
    Protocol,
    runtime_checkable,
    ParamSpec,
)

from domprob.base_exc import DomprobException
from domprob.observations.observation import ObservationProtocol

_P = ParamSpec("_P")
_R = TypeVar("_R", bound=Any)


@runtime_checkable
class DispatcherProtocol(Protocol):
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
        ...     def dispatch(self, observation: ObservationProtocol[int, str]) -> str:
        ...         return "Processed observation"
        ...
        ...     def __repr__(self) -> str:
        ...         return "ConcreteDispatcher()"
        ...
        >>> dispatcher = ConcreteDispatcher()
        >>> assert isinstance(dispatcher, DispatcherProtocol)
    """

    def dispatch(
        self, observation: ObservationProtocol[[_P.args, _P.kwargs], _R]
    ) -> _R:
        # noinspection PyShadowingNames
        """Dispatch an observation and return a result.

        Args:
            observation (`ObservationProtocol[_P, _R]`): The
                observation to process.

        Returns:
            `_R`: The result of processing the observation.

        Example:
            >>> from domprob import announcement, BaseObservation
            >>> from domprob.dispatchers.dispatcher import DispatcherProtocol
            >>> from domprob.observations.observation import ObservationProtocol
            >>>
            >>> class MyDispatcher:
            ...     @staticmethod
            ...     def dispatch(observation: ObservationProtocol[int, str]) -> str:
            ...         return "Handled"
            ...
            >>> dispatcher = MyDispatcher()
            >>>
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> class Obs(BaseObservation):
            ...     @announcement(SomeInstrument)
            ...     def foo(self, instrument: SomeInstrument) -> str:
            ...         pass
            ...
            >>> result = dispatcher.dispatch(Obs())
            >>> print(result)
            Handled
        """

    def __repr__(self) -> str:
        """Return a string representation of the dispatcher.

        Returns:
            str: The string representation of the dispatcher.
        """


class DispatcherException(DomprobException):
    """Base exception for errors occurring within dispatchers.

    This exception is raised when an error occurs while processing
    observations within a dispatcher.

    It inherits from `DomprobException`, allowing it to be caught
    alongside other domain-specific exceptions.
    """

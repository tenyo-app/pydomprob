from typing import Any

from domprob.consumers.consumer import ConsumerProtocol
from domprob.dispatchers.dispatcher import DispatcherProtocol
from domprob.observations.observation import ObservationProtocol


class BasicDispatcher(DispatcherProtocol):
    # pylint: disable=line-too-long
    """Dispatches observations to registered consumers.

    Args:
        *consumers (`tuple[ConsumerProtocol, ...]`): Variable number of
            consumer instances.

    Example:
        >>> from abc import ABC, abstractmethod
        >>> from domprob.consumers.basic import BasicConsumer
        >>>
        >>> class BaseInstrument(ABC):
        ...     @abstractmethod
        ...     def add(self):
        ...         pass
        ...
        >>> class LoggerInstrument:
        ...     @staticmethod
        ...     def add():
        ...         return "Log message added!"
        ...
        >>> class AnalyticsInstrument:
        ...     @staticmethod
        ...     def add():
        ...         return "Analytics entry added!"
        ...
        >>> consumer = BasicConsumer(LoggerInstrument(), AnalyticsInstrument())
        >>> dispatcher = BasicDispatcher(consumer)
        >>>
        >>> dispatcher
        BasicDispatcher(consumers=(BasicConsumer(instruments=('<domprob.dispatchers.basic.LoggerInstrument object at 0x...>', '<domprob.dispatchers.basic.AnalyticsInstrument object at 0x...>')),))
        >>>
        >>> from domprob import sensor, BaseObservation
        >>>
        >>> class SomeObservation(BaseObservation):
        ...     @sensor(LoggerInstrument)
        ...     @sensor(AnalyticsInstrument)
        ...     def foo(self, instrument: BaseInstrument) -> None:
        ...         print(instrument.add())
        ...
        >>> obs = SomeObservation()
        >>> dispatcher.dispatch(obs)
        Analytics entry added!
        Log message added!
    """

    def __init__(self, *consumers: ConsumerProtocol) -> None:
        self.consumers = consumers

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.consumers == other.consumers

    def __hash__(self) -> int:
        return hash(self.consumers)

    def dispatch(self, observation: ObservationProtocol) -> None:
        # noinspection PyShadowingNames
        # pylint: disable=line-too-long
        """Dispatch an observation to all available consumers.

        This method calls `consume` on consumers to handle the
        observation passed.

        Args:
            observation (_Obs): The observation to dispatch.

        Example:
            >>> from abc import ABC, abstractmethod
            >>> from domprob.consumers.basic import BasicConsumer
            >>>
            >>> class BaseInstrument(ABC):
            ...     @abstractmethod
            ...     def add(self):
            ...         pass
            ...
            >>> class LoggerInstrument:
            ...     @staticmethod
            ...     def add():
            ...         return "Log message added!"
            ...
            >>> class AnalyticsInstrument:
            ...     @staticmethod
            ...     def add():
            ...         return "Analytics entry added!"
            ...
            >>>
            >>> consumer = BasicConsumer(LoggerInstrument(), AnalyticsInstrument())
            >>> dispatcher = BasicDispatcher(consumer)
            >>>
            >>> dispatcher
            BasicDispatcher(consumers=(BasicConsumer(instruments=('<domprob.dispatchers.basic.LoggerInstrument object at 0x...>', '<domprob.dispatchers.basic.AnalyticsInstrument object at 0x...>')),))
            >>>
            >>> from domprob import sensor, BaseObservation
            >>>
            >>> class SomeObservation(BaseObservation):
            ...     @sensor(LoggerInstrument)
            ...     @sensor(AnalyticsInstrument)
            ...     def foo(self, instrument: BaseInstrument) -> None:
            ...         print(instrument.add())
            ...
            >>> obs = SomeObservation()
            >>> dispatcher.dispatch(obs)
            Analytics entry added!
            Log message added!
        """
        for consumer in self.consumers:
            consumer.consume(observation)

    def __repr__(self) -> str:
        # pylint: disable=line-too-long
        """Return a string representation of the dispatcher.

        Returns:
            str: A string representation of the dispatcher and its
                consumers.

        Example:
            >>> from abc import ABC, abstractmethod
            >>> from domprob.consumers.basic import BasicConsumer
            >>>
            >>> class BaseInstrument(ABC):
            ...     @abstractmethod
            ...     def add(self):
            ...         pass
            ...
            >>> class LoggerInstrument:
            ...     @staticmethod
            ...     def add():
            ...         return "Log message added!"
            ...
            >>> class AnalyticsInstrument:
            ...     @staticmethod
            ...     def add():
            ...         return "Analytics entry added!"
            ...
            >>> consumer = BasicConsumer(LoggerInstrument(), AnalyticsInstrument())
            >>> dispatcher = BasicDispatcher(consumer)
            >>> repr(dispatcher)
            "BasicDispatcher(consumers=(BasicConsumer(instruments=('<domprob.dispatchers.basic.LoggerInstrument object at 0x...>', '<domprob.dispatchers.basic.AnalyticsInstrument object at 0x...>')),))"
        """
        return f"{self.__class__.__name__}(consumers={self.consumers!r})"

from __future__ import annotations

import logging
from typing import Any

from domprob.consumers.basic import BasicConsumer
from domprob.dispatchers.basic import BasicDispatcher
from domprob.dispatchers.dispatcher import DispatcherProtocol
from domprob.observations.observation import ObservationProtocol


class Probe:
    # noinspection PyShadowingNames
    """
    A class representing a probes that facilitates the dispatching of
    observations.

    Attributes:
        dispatcher (_DispT): The dispatcher responsible for handling
            observations.

    Example:
        >>> from domprob import (
        ...     sensor,
        ...     BaseObservation,
        ...     BasicConsumer,
        ...     BasicDispatcher,
        ...     Probe,
        ... )
        >>>
        >>> class SomeInstrument:
        ...
        ...     @staticmethod
        ...     def call(msg: str) -> None:
        ...         print(msg)
        ...
        >>>
        >>> class SampleObservation(BaseObservation):
        ...
        ...     @staticmethod
        ...     @sensor(SomeInstrument)
        ...     def sense_msg(some_instrument: SomeInstrument) -> None:
        ...         some_instrument.call("Sensed!")
        ...
        >>> consumer = BasicConsumer(SomeInstrument())
        >>> dispatcher = BasicDispatcher(consumer)
        >>> probes = Probe(dispatcher)
        >>>
        >>> probes.observe(SampleObservation())
        Sensed!
    """

    def __init__(self, dispatcher: DispatcherProtocol) -> None:
        self.dispatcher = dispatcher

    def __eq__(self, other: Any) -> bool:
        """Determines if two `Probe` instances are equal.

        Probes are considered equal if they are of the same type and
        have the same dispatcher.

        Args:
            other (Any): The object to compare with.

        Returns:
            bool: True if the probes are equal, False otherwise.

        Example:
            >>> from domprob import BasicDispatcher
            >>>
            >>> probe1 = Probe(BasicDispatcher())
            >>> probe2 = Probe(BasicDispatcher())
            >>>
            >>> assert probe1 == probe2
        """
        if not isinstance(other, type(self)):
            return False
        return (type(self) is type(other)) and (
            self.dispatcher == other.dispatcher
        )

    def __hash__(self) -> int:
        """Computes the hash value of the `Probe` instance.

        The hash is based on the dispatcher's hash, ensuring that
        probes with the same dispatcher have the same hash.

        Returns:
            int: The hash value of the instance.

        Example:
            >>> from domprob import BasicDispatcher
            >>>
            >>> probe1 = Probe(BasicDispatcher())
            >>> probe2 = Probe(BasicDispatcher())
            >>>
            >>> hash1 = hash(probe1)
            >>> hash2 = hash(probe2)
            >>>
            >>> assert hash1 == hash2
        """
        return hash(self.dispatcher)

    def observe(self, observation: ObservationProtocol) -> None:
        """Dispatches an observation using the associated dispatcher.

        Args:
            observation (ObservationProtocol): The observation to be
                dispatched.
        """
        self.dispatcher.dispatch(observation)

    def __repr__(self) -> str:
        # noinspection PyShadowingNames
        """Returns a string representation of the `Probe` instance.

        Returns:
            str: A formatted string representing the instance.

        Example:
            >>> from domprob import BasicDispatcher
            >>>
            >>> probes = Probe(BasicDispatcher())
            >>> repr(probes)
            'Probe(dispatcher=BasicDispatcher(consumers=()))'
        """
        return f"{self.__class__.__name__}(dispatcher={self.dispatcher!r})"


def get_probe(*instruments: Any) -> Probe:
    # pylint: disable=line-too-long
    """Creates a `Probe` instance with the provided instruments.

    If no instruments are provided, it defaults to using a default
    `logging.Logger` instance.

    Args:
        *instruments (_InstrumT): The instrument implementations to be
            used to fulfil the observations.

    Returns:
        Probe: A new `Probe` instance initialized with a
            `BasicDispatcher`.

    Example:
        >>> from domprob import get_probe
        >>>
        >>> # Create a probes with a custom instrument
        >>> custom_probe = get_probe(logging.getLogger("custom"))
        >>> custom_probe
        Probe(dispatcher=BasicDispatcher(consumers=(BasicConsumer(instruments=('<Logger custom (WARNING)>',)),)))
        >>>
        >>> # Create a probes with default instruments
        >>> default_probe = get_probe()
        >>> default_probe
        Probe(dispatcher=BasicDispatcher(consumers=(BasicConsumer(instruments=('<Logger default (DEBUG)>',)),)))
    """
    if not instruments:
        log = logging.getLogger("default")
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s: %(message)s"
        )
        handler.setFormatter(formatter)
        log.addHandler(handler)
        log.setLevel(logging.DEBUG)
        instruments = (log,)
    consumer = BasicConsumer(*instruments)
    dispatcher = BasicDispatcher(consumer)

    return Probe(dispatcher)


probe = get_probe()
"""The default probe.

Example:
    >>> from domprob.probes.probe import probe
    >>> 
    >>> probe
    Probe(dispatcher=BasicDispatcher(instruments=('<RootLogger root (WARNING)>',)))
"""

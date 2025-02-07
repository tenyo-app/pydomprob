from __future__ import annotations

import logging
from typing import Any

from domprob.dispatchers.dispatcher import DispatcherProtocol
from domprob.dispatchers.basic import BasicDispatcher
from domprob.observations.observation import ObservationProtocol


class Probe:
    # noinspection PyShadowingNames
    """
    A class representing a probe that facilitates the dispatching of
    observations.

    Attributes:
        dispatcher (_DispT): The dispatcher responsible for handling
            observations.

    Example:
        >>> from domprob import announcement, BaseObservation, Probe
        >>> from domprob.dispatchers.basic import BasicDispatcher
        >>>
        >>> class SomeInstrument:
        ...
        ...     def call(self, msg: str) -> None:
        ...         print(msg)
        ...
        >>>
        >>> class SampleObservation(BaseObservation):
        ...
        ...     @announcement(SomeInstrument)
        ...     def announce(self, some_instrument: SomeInstrument) -> None:
        ...         some_instrument.call("Announcement!")
        ...
        >>>
        >>> dispatcher = BasicDispatcher(SomeInstrument())
        >>> probe = Probe(dispatcher)
        >>>
        >>> probe.observe(SampleObservation())
        Announcement!
    """

    def __init__(self, dispatcher: DispatcherProtocol) -> None:
        self.dispatcher = dispatcher

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, type(self)):
            return False
        return (type(self) is type(other)) and (
            self.dispatcher == other.dispatcher
        )

    def __hash__(self) -> int:
        return hash(self.dispatcher)

    def observe(self, observation: ObservationProtocol) -> None:
        """Dispatches an observation using the associated dispatcher.

        Args:
            observation (ObservationProtocol): The observation to be
                dispatched.
        """
        self.dispatcher.dispatch(observation)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(dispatcher={self.dispatcher!r})"


_INSTRUMENTS: tuple[Any, ...] = (logging.getLogger(),)


def probe(*instruments: Any) -> Probe:
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
        >>> from domprob.probes.probe import probe
        >>>
        >>> # Create a probe with a custom instrument
        >>> custom_probe = probe(logging.getLogger("custom"))
        >>> custom_probe
        Probe(dispatcher=BasicDispatcher(instruments=('(<Logger custom (WARNING)>,)',)))
        >>>
        >>> # Create a probe with default instruments
        >>> default_probe = probe()
        >>> default_probe
        Probe(dispatcher=BasicDispatcher(instruments=('(<RootLogger root (WARNING)>,)',)))
    """
    dispatcher = BasicDispatcher(instruments or _INSTRUMENTS)
    return Probe(dispatcher)

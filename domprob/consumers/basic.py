from collections.abc import Iterator, Collection, Generator
from typing import Any, TypeVar, ParamSpec, Generic

from domprob.consumers.consumer import ConsumerProtocol
from domprob.announcements.method import AnnouncementMethod
from domprob.consumers.consumer import ConsumerException
from domprob.observations.observation import ObservationProtocol


_Instrument = TypeVar("_Instrument", bound=Any)


class InstrumentImpRegistry(Collection[_Instrument]):
    """Registry for instrument implementations, allowing lookup and
    caching.

    This class acts as a collection that stores instruments and
    supports:

    - Efficient retrieval of instruments by type.
    - Caching of previously looked-up instruments for performance
      optimization.

    Args:
        *instruments (`_Instrument`): Variable number of instrument
            instances to store.

    Example:
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
        >>> logger = LoggerInstrument()
        >>> analytics = AnalyticsInstrument()
        >>>
        >>> registry = InstrumentImpRegistry(logger, analytics)
        >>> logger_ = registry.get(LoggerInstrument)
        >>>
        >>> logger == logger_
        True
        >>> print(registry.get(object))
        None
    """

    def __init__(self, *instruments: _Instrument) -> None:
        self._instrums = instruments
        self._cache: dict[type[_Instrument], _Instrument] = {}

    def __contains__(self, item: object) -> bool:
        """Check if an instrument exists in the registry.

        Args:
            item: The instrument instance or class to check.

        Returns:
            bool: True if the instrument is present, otherwise False.

        Example:
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
            >>> logger = LoggerInstrument()
            >>> analytics = AnalyticsInstrument()
            >>>
            >>> registry = InstrumentImpRegistry(logger, analytics)
            >>> logger in registry
            True
            >>> object in registry
            False
        """
        return item in self._instrums

    def __hash__(self) -> int:
        return hash(self._instrums)

    def __iter__(self) -> Iterator[_Instrument]:
        """Iterate over stored instruments.

        Returns:
            Iterator[_Instrument]: An iterator over the instruments.

        Example:
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
            >>> logger = LoggerInstrument()
            >>> analytics = AnalyticsInstrument()
            >>>
            >>> registry = InstrumentImpRegistry(logger, analytics)
            >>>
            >>> for instrument in registry:
            ...     print(instrument.add())
            ...
            Log message added!
            Analytics entry added!
        """
        yield from self._instrums

    def __len__(self) -> int:
        """Return the number of stored instruments.

        Returns:
            int: The number of instruments in the registry.

        Example:
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
            >>> logger = LoggerInstrument()
            >>> analytics = AnalyticsInstrument()
            >>>
            >>> registry = InstrumentImpRegistry(logger, analytics)
            >>>
            >>> len(registry)
            2
        """
        return len(self._instrums)

    @staticmethod
    def _is_hashable(obj: Any) -> bool:
        """Check if an object is hashable.

        Args:
            obj (`Any`): The object to check.

        Returns:
            `bool`: True if the object is hashable, False otherwise.
        """
        try:
            hash(obj)
        except TypeError:
            return False
        return True

    def get(
        self, instrument_cls: type[_Instrument], required: bool = False
    ) -> _Instrument | None:
        # pylint: disable=line-too-long
        """Retrieve an instrument instance by its class type.

        If the instrument class is hashable, results are cached for
        efficiency.

        Args:
            instrument_cls: The class type of the instrument to
                retrieve.
            required: If `True`, raises a `KeyError` if the instrument
                is not found. If `False`, returns `None`.

        Returns:
            _Instrument | None: The retrieved instrument instance or
                `None` if not found.

        Raises:
            KeyError: If `required` is `True` and the instrument is not
                found.

        Example:
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
            >>> logger = LoggerInstrument()
            >>> analytics = AnalyticsInstrument()
            >>>
            >>> registry = InstrumentImpRegistry(logger)
            >>>
            >>> registry.get(LoggerInstrument).add()
            'Log message added!'
            >>> registry.get(AnalyticsInstrument, required=True)
            Traceback (most recent call last):
                ...
            KeyError: 'Instrument `AnalyticsInstrument` not found in available implementations: `<domprob.consumers.basic.LoggerInstrument object at 0x...>`'
        """
        if self._is_hashable(instrument_cls) and instrument_cls in self._cache:
            return self._cache[instrument_cls]
        for instrum in self._instrums:
            # pylint: disable=unidiomatic-typecheck
            if type(instrum) is instrument_cls:
                if self._is_hashable(instrument_cls):
                    self._cache[instrument_cls] = instrum
                return instrum
        if required:
            imp_str = ", ".join(f"`{repr(i)}`" for i in self._instrums) or None
            raise KeyError(
                f"Instrument `{instrument_cls.__name__}` not found in "
                f"available implementations: {imp_str}"
            )
        return None

    def __repr__(self) -> str:
        """Return a string representation of the registry.

        Returns:
            `str`: The string representation of the registry.
        """
        return f"{self.__class__.__name__}(num_instruments={len(self)})"


_P = ParamSpec("_P")
_R = TypeVar("_R", bound=Any)


class ReqInstrumException(ConsumerException):
    """Exception raised when a required instrument is missing an
    implementation of the same type for an observation announcement.

    An instrument is marked as required with the `required`
    flag in the `@announcement` decorator:

    >>> from domprob import announcement, BaseObservation
    >>>
    >>> class SomeObservation(BaseObservation):
    ...
    ...     @announcement(..., required=True)
    ...     def some_method(self, instrument: ...) -> None:
    ...         ...
    ...

    Args:
        observation (_Obs): The observation instance where the missing
            instrument was required.
        announcement (_Ann): The announcement method that failed due to
            the missing instrument.
        req_supp_instr (type[_Instrument]): The instrument type that
            was expected but not found.
        *instrum_imps (_Instrument): The available instrument instances
            at the time of the failure.
    """

    def __init__(
        self,
        observation: ObservationProtocol,
        announcement: AnnouncementMethod,
        req_supp_instrum: type[Any],
        *instrum_imps: Any,
    ) -> None:
        self.observation = observation
        self.announcement = announcement
        self.req_supp_instr = req_supp_instrum
        self.instrum_imps = instrum_imps
        super().__init__(self.msg)

    @property
    def msg(self) -> str:
        """Constructs a descriptive error message for the exception.

        Returns:
            str: A formatted string detailing the missing instrument,
                the observation method where it was required, and the
                available instrument implementations.
        """
        req_name = self.req_supp_instr.__name__
        meth_name = self.announcement.meth.__name__
        obs_meth = f"{self.observation.__class__.__name__}.{meth_name}(...)"
        imps_str = ", ".join([f"`{repr(i)}`" for i in self.instrum_imps])
        return (
            f"Required instrument `{req_name}` in `{obs_meth}` is "
            f"missing from available implementations: {imps_str or None}"
        )


class BasicConsumer(ConsumerProtocol, Generic[_Instrument]):

    def __init__(self, *instruments: _Instrument) -> None:
        self.instrums = InstrumentImpRegistry(*instruments)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, type(self)):
            return False
        return tuple(self.instrums) == tuple(other.instrums)

    def __hash__(self) -> int:
        return hash(self.instrums)

    def consume(self, observation: ObservationProtocol) -> None:
        for ann in observation.announcements():
            for instrum_imp in self.instrum_imps(observation, ann):
                if instrum_imp is not None:
                    ann.meth(observation, instrum_imp)

    def instrum_imps(
        self,
        observation: ObservationProtocol,
        announcement: AnnouncementMethod,
    ) -> Generator[_Instrument | None, None, None]:
        for supp_instrum, req in announcement.supp_instrums:
            try:
                instrum_imp = self.instrums.get(supp_instrum, req)
            except KeyError as e:
                raise ReqInstrumException(
                    observation, announcement, supp_instrum, *self.instrums
                ) from e
            yield instrum_imp

    def __repr__(self) -> str:
        instrum_imps = tuple(repr(i) for i in self.instrums)
        return f"{self.__class__.__name__}(instruments={instrum_imps!r})"

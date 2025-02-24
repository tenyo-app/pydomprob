from collections.abc import Collection, Generator, Iterator
from typing import Any, Generic, ParamSpec, TypeVar

from domprob.consumers.consumer import ConsumerException, ConsumerProtocol
from domprob.observations.observation import ObservationProtocol
from domprob.sensors.meth import SensorMethod

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
        *instruments (`_Instrum`): Variable number of instrument
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
            Iterator[_Instrum]: An iterator over the instruments.

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
            _Instrum | None: The retrieved instrument instance or
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
    implementation of the same type for an observation sensors.

    An instrument is marked as required with the `required`
    flag in the `@sensors` decorator:

    >>> from domprob import sensor, BaseObservation
    >>>
    >>> class SomeObservation(BaseObservation):
    ...
    ...     @sensor(..., required=True)
    ...     def some_method(self, instrument: ...) -> None:
    ...         ...
    ...

    Args:
        observation (_Obs): The observation instance where the missing
            instrument was required.
        sensor (SensorMethod): The sensors method that failed due to
            the missing instrument.
        req_supp_instr (type[_Instrum]): The instrument type that
            was expected but not found.
        *instrum_imps (_Instrum): The available instrument instances
            at the time of the failure.
    """

    def __init__(
        self,
        observation: ObservationProtocol,
        sensor: SensorMethod,
        req_supp_instrum: type[Any],
        *instrum_imps: Any,
    ) -> None:
        self.observation = observation
        self.sensor = sensor
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
        meth_name = self.sensor.meth.__name__
        obs_meth = f"{self.observation.__class__.__name__}.{meth_name}(...)"
        imps_str = ", ".join([f"`{repr(i)}`" for i in self.instrum_imps])
        return (
            f"Required instrument `{req_name}` in `{obs_meth}` is "
            f"missing from available implementations: {imps_str or None}"
        )


class BasicConsumer(ConsumerProtocol, Generic[_Instrument]):
    """A consumer that processes observations by applying instrument
    implementations.

    This class acts as a consumer that takes in instrument
    implementations and processes observations by executing their
    associated sensors methods with the relevant instrument.

    Args:
        *instruments (_Instrum): One or more instrument instances.

    Example:
        >>> from domprob import sensor, BaseObservation
        >>>
        >>> class LoggerInstrument:
        ...     @staticmethod
        ...     def log(message: str):
        ...         print(f"LOG: {message}")
        ...
        >>> class SomeObservation(BaseObservation):
        ...     @sensor(LoggerInstrument)
        ...     def sense_event(self, instrument: LoggerInstrument):
        ...         instrument.log("Event sensed!")
        ...
        >>> logger = LoggerInstrument()
        >>> consumer = BasicConsumer(logger)
        >>>
        >>> consumer.consume(SomeObservation())
        LOG: Event sensed!
    """

    def __init__(self, *instruments: _Instrument) -> None:
        self.instrums = InstrumentImpRegistry(*instruments)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, type(self)):
            return False
        return tuple(self.instrums) == tuple(other.instrums)

    def __hash__(self) -> int:
        return hash(self.instrums)

    def consume(self, observation: ObservationProtocol) -> None:
        """Processes an observation by invoking the relevant instrument
        methods.

        The method iterates through the observation’s sensors and
        applies the required instrument implementations.

        Args:
            observation (ObservationProtocol): The observation to
                process.
        """
        for ann in observation.sensors():
            for instrum_imp in self.instrum_imps(observation, ann):
                if instrum_imp is not None:
                    if ann.is_static:
                        ann.meth(instrum_imp)  # Executes sensors
                    else:
                        ann.meth(observation, instrum_imp)

    def instrum_imps(
        self,
        observation: ObservationProtocol,
        sensor: SensorMethod,
    ) -> Generator[_Instrument | None, None, None]:
        # noinspection PyCallingNonCallable
        """Retrieves instrument implementations required for sensors.

        Args:
            observation (ObservationProtocol): The observation being
                processed.
            sensor (SensorMethod): The sensors to
                handle.

        Yields:
            _Instrum | None: The appropriate instrument
                implementation or `None` if non-required instrument
                implementations are missing.

        Raises:
            ReqInstrumException: If a required instrument is missing.

        Example:
            >>> from domprob import sensor, BaseObservation
            >>> from domprob.sensors.meth import SensorMethod
            >>>
            >>> class LoggerInstrument:
            ...     @staticmethod
            ...     def log(message: str):
            ...         print(f"LOG: {message}")
            ...
            >>> class SomeObservation(BaseObservation):
            ...     @staticmethod
            ...     @sensor(LoggerInstrument)
            ...     def sense_observation(instrument: LoggerInstrument):
            ...         instrument.log("Event sensed!")
            ...
            >>> logger = LoggerInstrument()
            >>> consumer = BasicConsumer(logger)
            >>> sensor_meth = SensorMethod(SomeObservation.sense_observation)
            >>>
            >>> list(consumer.instrum_imps(SomeObservation(), sensor_meth))
            [<domprob.consumers.basic.LoggerInstrument object at 0x...>]
        """
        for supp_instrum, req in sensor.supp_instrums:
            try:
                instrum_imp = self.instrums.get(supp_instrum, req)
            except KeyError as e:
                raise ReqInstrumException(
                    observation, sensor, supp_instrum, *self.instrums
                ) from e
            yield instrum_imp

    def __repr__(self) -> str:
        instrum_imps = tuple(repr(i) for i in self.instrums)
        return f"{self.__class__.__name__}(instruments={instrum_imps!r})"

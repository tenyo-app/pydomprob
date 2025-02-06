from collections.abc import Collection, Iterator
from typing import TypeVar, Any, Generic, ParamSpec, TypeAlias

from domprob.dispatchers.dispatcher import DispatcherException
from domprob.announcements.method import AnnouncementMethod
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
        self.instrums = tuple(instruments)
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
        return item in self.instrums

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
        yield from self.instrums

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
        return len(self.instrums)

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
            KeyError: 'Instrument `AnalyticsInstrument` not found in available implementations: `<domprob.dispatchers.basic.LoggerInstrument object at 0x...>`'
        """
        if self._is_hashable(instrument_cls) and instrument_cls in self._cache:
            return self._cache[instrument_cls]
        for instrum in self.instrums:
            # pylint: disable=unidiomatic-typecheck
            if type(instrum) is instrument_cls:
                if self._is_hashable(instrument_cls):
                    self._cache[instrument_cls] = instrum
                return instrum
        if required:
            imps_str = ", ".join(f"`{repr(i)}`" for i in self.instrums) or None
            raise KeyError(
                f"Instrument `{instrument_cls.__name__}` not found in "
                f"available implementations: {imps_str}"
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

# Type alias to defer ParamSpec type resolution and simplify type
# checking for PyCharm & Mypy due to Generic chaining. Using aliases
# prevents direct generic resolution in function signatures while
# maintaining full type safety
_Obs: TypeAlias = ObservationProtocol[_P, _R]

_Ann: TypeAlias = AnnouncementMethod[_P, _R]


class ReqInstrumException(DispatcherException):
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
        observation: _Obs,
        announcement: _Ann,
        req_supp_instrum: type[_Instrument],
        *instrum_imps: _Instrument,
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


class BasicDispatcher(Generic[_Instrument, _P, _R]):
    # pylint: disable=line-too-long
    """Dispatches observations to registered instruments.

    This class manages:
    - Finding the appropriate instrument for a given observation.
    - Dispatching announcements to the relevant instruments.

    Args:
        *instruments (`_Instrument`): Variable number of instrument
            instances.

    Example:
        >>> from abc import ABC, abstractmethod
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
        >>> dispatcher = BasicDispatcher(LoggerInstrument(), AnalyticsInstrument())
        >>> dispatcher
        BasicDispatcher(<domprob.dispatchers.basic.LoggerInstrument object at 0x...>, <domprob.dispatchers.basic.AnalyticsInstrument object at 0x...>)
        >>>
        >>> from domprob import announcement, BaseObservation
        >>>
        >>> class SomeObservation(BaseObservation):
        ...     @announcement(LoggerInstrument)
        ...     @announcement(AnalyticsInstrument)
        ...     def foo(self, instrument: BaseInstrument) -> None:
        ...         print(instrument.add())
        ...
        >>> obs = SomeObservation()
        >>> dispatcher.dispatch(obs)
        Analytics entry added!
        Log message added!
    """

    def __init__(self, *instruments: _Instrument) -> None:
        self.instrums = InstrumentImpRegistry(*instruments)
        self.cached_instrums: dict[type[_Instrument], _Instrument] = {}

    @staticmethod
    def _dispatch_instrum_ann(
        observation: _Obs,
        announcement: _Ann,
        instrument: _Instrument | None,
    ) -> None:
        """Invoke an announcement method on an instrument.

        This method triggers the specified announcement method
        on the given instrument instance if it is available.

        Args:
            observation (_Obs): The observation being processed.
            announcement (_Ann): The announcement method to invoke.
            instrument (_Instrument | None): The target instrument
                instance, if available.
        """
        if instrument is not None:
            announcement.meth(observation, instrument)

    def _dispatch_ann(
        self,
        observation: _Obs,
        announcement: _Ann,
    ) -> None:
        """Process an announcement by identifying the required
        instrument.

        This method retrieves the correct instrument instance based
        on the announcement and calls `_instrum_announce`.

        Args:
            observation (_Obs): The observation being processed.
            announcement (_Ann): The announcement method to invoke.
        """
        for supp_instrum, required in announcement.supp_instrums:
            try:
                instrum_imp = self.instrums.get(supp_instrum, required)
            except KeyError as e:
                raise ReqInstrumException(
                    observation, announcement, supp_instrum, *self.instrums
                ) from e
            self._dispatch_instrum_ann(observation, announcement, instrum_imp)

    def dispatch(self, observation: _Obs) -> None:
        # pylint: disable=line-too-long
        """Dispatch an observation to all applicable instruments.

        This method retrieves all announcements from the observation
        and processes them.

        Args:
            observation (_Obs): The observation to process.

        Example:
            >>> from abc import ABC, abstractmethod
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
            >>> dispatcher = BasicDispatcher(LoggerInstrument(), AnalyticsInstrument())
            >>> dispatcher
            BasicDispatcher(<domprob.dispatchers.basic.LoggerInstrument object at 0x...>, <domprob.dispatchers.basic.AnalyticsInstrument object at 0x...>)
            >>>
            >>> from domprob import announcement, BaseObservation
            >>>
            >>> class SomeObservation(BaseObservation):
            ...     @announcement(LoggerInstrument)
            ...     @announcement(AnalyticsInstrument)
            ...     def foo(self, instrument: BaseInstrument) -> None:
            ...         print(instrument.add())
            ...
            >>> obs = SomeObservation()
            >>> dispatcher.dispatch(obs)
            Analytics entry added!
            Log message added!
        """
        for ann in observation.announcements():
            self._dispatch_ann(observation, ann)

    def __repr__(self) -> str:
        # pylint: disable=line-too-long
        """Return a string representation of the dispatcher.

        Returns:
            str: A string representation of the dispatcher and its
                instruments.

        Example:
            >>> from abc import ABC, abstractmethod
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
            >>> dispatcher = BasicDispatcher(LoggerInstrument(), AnalyticsInstrument())
            >>> repr(dispatcher)
            'BasicDispatcher(<domprob.dispatchers.basic.LoggerInstrument object at 0x...>, <domprob.dispatchers.basic.AnalyticsInstrument object at 0x...>)'
        """
        instrum_imps_str = ", ".join(repr(i) for i in self.instrums)
        return f"{self.__class__.__name__}({instrum_imps_str})"

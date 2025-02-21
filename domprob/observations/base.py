from __future__ import annotations

import inspect
from abc import ABC
from collections.abc import Generator, Set
from typing import Any, ParamSpec, TypeVar

from domprob.observations.observation import ObservationProtocol
from domprob.sensors.meth import SensorMethod

# Typing helpers: defines a @sensor's method signature
_P = ParamSpec("_P")
_R = TypeVar("_R")
_Sensor = SensorMethod[_P, _R]


class SensorSet(Set[_Sensor]):
    """A custom set-like collection for storing `SensorMethod`
    instances.

    This class ensures unique sensors methods and provides
    set-like behavior for iteration, containment checks, and length
    retrieval.

    Args:
        *sensor_methods (_SensorSig): One or more sensors
            method instances.

    Example:
        >>> from domprob import sensor
        >>>
        >>> class MyObservation:
        ...
        ...     @sensor(...)
        ...     def sense_hello(self, _):
        ...         pass
        ...
        ...     def normal_method(self, _):
        ...         pass
        ...
        >>> meth = SensorMethod(MyObservation.sense_hello)
        >>> sensor_set = SensorSet(meth, meth)
        >>> len(sensor_set)
        1
    """

    def __init__(self, *sensor_methods: _Sensor) -> None:
        self._sensor_methods = set(sensor_methods)

    @classmethod
    def from_observation(cls, observation_cls: Any) -> SensorSet:
        """Creates an SensorSet by extracting sensors
        methods from a given class.

        This method inspects the provided class, identifies methods
        that qualify as sensors methods using
        `SensorMethod.from_callable`, and includes them in the returned
        `SensorSet`.

        Args:
            observation_cls (Any): The class to inspect for
                sensors methods.

        Returns:
            SensorSet: A set of extracted sensors methods.

        Example:
            >>> from domprob import sensor
            >>>
            >>> class MyObservation:
            ...
            ...     @sensor(...)
            ...     def sense_hello(self, _):
            ...         pass
            ...
            ...     def normal_method(self, _):
            ...         pass
            ...
            >>> sensor_set = SensorSet.from_observation(MyObservation)
            >>> len(sensor_set)
            1
        """
        meths = []
        for _, meth in inspect.getmembers(observation_cls, inspect.isfunction):
            sensor_meth = SensorMethod.from_callable(meth)
            if sensor_meth is not None:
                meths.append(sensor_meth)
        return cls(*meths)

    def __contains__(self, item: Any) -> bool:
        """Checks if a given sensors method exists in the set.

        Args:
            item (Any): The item to check.

        Returns:
            bool: True if `item` is an instance of `SensorMethod` and
                exists in the set, False otherwise.
        """
        if not isinstance(item, SensorMethod):
            return False
        return item in self._sensor_methods

    def __iter__(self) -> Generator[_Sensor, None, None]:
        """Returns an iterator over the sensors methods in the
        set.

        Yields:
            _SensorSig: Each sensors method stored in the set.
        """
        yield from self._sensor_methods

    def __len__(self) -> int:
        """Returns the number of sensors methods in the set.

        Returns:
            int: The count of stored sensors methods.
        """
        return len(self._sensor_methods)

    def __repr__(self) -> str:
        """Returns a string representation of the SensorSet.

        Returns:
            str: A string describing the number of stored
                sensors.
        """
        return f"{self.__class__.__name__}(num_sensors={len(self)})"


class BaseObservation(ABC, ObservationProtocol):
    """Base class for observations.

    Attributes:
        __slots__ (tuple): Prevents the creation of instance __dict__
            to keep memory footprint low.

    Example:
        >>> from domprob import sensor, BaseObservation
        >>>
        >>> class SomeInstrument:
        ...     pass
        ...
        >>> class MyObservation(BaseObservation):
        ...     @sensor(SomeInstrument)
        ...     def my_method(self, instrument: SomeInstrument) -> str:
        ...         pass
        ...
        >>> observation = MyObservation()
        >>> observation
        MyObservation(sensors=1)
    """

    # cached per observation cls imp - avoids recompute for each instance
    _sensors: SensorSet | None = None

    @classmethod
    def sensors(cls) -> SensorSet:
        """Yield sensors methods defined in the class.

        Uses **lazy evaluation** to avoid unnecessary memory
        consumption.

        Yields:
            _SensorSig: Sensor method instances.

        Example:
            >>> from domprob import sensor, BaseObservation
            >>>
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> class MyObservation(BaseObservation):
            ...     @sensor(SomeInstrument)
            ...     def event_occurred(self, instrument: SomeInstrument) -> None:
            ...         pass
            ...
            >>> gen = MyObservation.sensors()
            >>> list(gen)
            [SensorMethod(meth=<function MyObservation.event_occurred at 0x...>)]
        """
        if cls._sensors is None:
            cls._sensors = SensorSet.from_observation(cls)
        return cls._sensors

    def __len__(self) -> int:
        """Return the number of sensors.

        Returns:
            int: Count of sensors in the class.

        Example:
            >>> from domprob import sensor, BaseObservation
            >>>
            >>> class SomeInstrument:
            ...     pass
            ...
            >>> class MyObservation(BaseObservation):
            ...     @sensor(SomeInstrument)
            ...     def my_method(self, instrument: SomeInstrument) -> str:
            ...         pass
            ...
            >>> observation = MyObservation()
            >>> len(observation)
            1
        """
        return len(list(self.sensors()))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(sensors={len(self)})"

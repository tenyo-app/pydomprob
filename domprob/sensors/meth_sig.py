from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from inspect import Parameter, Signature, signature
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    ParamSpec,
    TypeAlias,
    TypeVar,
    get_type_hints,
    overload,
)

if sys.version_info >= (3, 11):
    from typing import Self  # pragma: no cover
else:
    from typing_extensions import Self  # pragma: no cover


# Typing helpers: sensor method
_P = ParamSpec("_P")
_R = TypeVar("_R")


if TYPE_CHECKING:
    from domprob.sensors.base_meth import BaseSensorMethod  # pragma: no cover

    _SensorMeth: TypeAlias = BaseSensorMethod[_P, _R]  # pragma: no cover


class InferSigInstrumBase(ABC):
    """Abstract base class for inferring the `instrum` parameter in a
    sensor method signature.

    Subclasses implement different strategies for identifying and
    renaming the `instrum` parameter within a method signature.

    Attributes:
        sig (SensorMethodSignature): The method signature being
            analyzed.
    """

    __slots__: tuple[str, ...] = ("sig",)

    def __init__(self, sig: SensorMethodSignature[Any, Any]) -> None:
        self.sig = sig

    @abstractmethod
    def infer(self) -> SensorMethodSignature[Any, Any] | None:
        """Attempts to infer and rename the `instrum` parameter in the
        method signature.

        Returns:
            SensorMethodSignature | None: The updated signature if
                inference is successful, otherwise `None`.
        """

    def __repr__(self) -> str:
        """Returns a string representation of the inference object.

        Returns:
            str: Human readable string representation of the inferer.
        """
        return f"{self.__class__.__name__}(sig={self.sig!r})"


# pylint: disable=too-few-public-methods
class InferSigInstrumByName(InferSigInstrumBase):
    """Infers the `instrum` parameter by checking for common name
    patterns.
    """

    def infer(self) -> SensorMethodSignature[Any, Any] | None:
        """Infers the `instrum` parameter based on 'instrum' or
        'instrument' param name matching.

        Returns:
            SensorMethodSignature | None: The updated signature if
                inference is successful, otherwise `None`.
        """
        if "instrum" in self.sig.keys:
            return self.sig
        if "instrument" in self.sig.keys:
            p = self.sig.rn_param("instrument", "instrum")
            return p
        return None


class InferSigInstrumByAnnotation(InferSigInstrumBase):
    """Infers the `instrum` parameter based on type annotations."""

    __slots__: tuple[str, ...] = ("_supp_instrums", "_type_hints")

    _supp_instrums: tuple[Any, ...] | None
    _type_hints: dict[str, Any] | None

    def __init__(self, sig: SensorMethodSignature[Any, Any]) -> None:
        super().__init__(sig)
        self._supp_instrums = None
        self._type_hints = None

    @property
    def supp_instrums(self) -> tuple[Any, ...]:
        """Gets the supported instrument types extracted from the
        sensor method.

        Returns:
            tuple[Any, ...]: A tuple of instrument types.
        """
        if self._supp_instrums is None:
            instrums = tuple(i for i, _ in self.sig.sensor.supp_instrums)
            self._supp_instrums = instrums
        return self._supp_instrums

    @property
    def type_hints(self) -> dict[str, Any]:
        """Retrieves type hints for the params defined in the sensor
        method.

        Returns:
            dict[str, Any]: A dictionary of parameter names and their
                corresponding type hints.
        """
        if self._type_hints is None:
            self._type_hints = get_type_hints(self.sig.sensor.meth)
        return self._type_hints

    def in_supp_instrums(self, param_type: Any) -> bool:
        """Checks if a parameter type matches any of the supported
        instruments.

        Args:
            param_type (Any): The parameter type to check.

        Returns:
            bool: `True` if the type matches a supported instrument,
                `False` otherwise.
        """
        if param_type is None:
            return False
        for instrum in self.supp_instrums:
            if (instrum == param_type) or issubclass(param_type, instrum):
                return True
        return False

    def get_type(self, param: Parameter) -> Any:
        """Extracts the type annotation of a parameter.

        Args:
            param (Parameter): The parameter object.

        Returns:
            Any: The resolved type annotation, `None` if unavailable.
        """
        if param.annotation is Parameter.empty:
            return None
        if isinstance(param.annotation, str):
            return self.type_hints.get(param.name)
        return param.annotation

    def infer(self) -> SensorMethodSignature[Any, Any] | None:
        """Infers the `instrum` parameter using type annotations.

        First checks to see if the method is static. If the method is
        not static, ignores first param.

        .. warning::
            Returns `None` if there are more than one parameter type
            annotations that match the supported instruments.

        Returns:
            SensorMethodSignature | None: The updated signature if
                inference is successful, otherwise `None`.
        """
        instrum_params = []
        for param in self.sig.values[0 if self.sig.sensor.is_static else 1 :]:
            param_type = self.get_type(param)
            instrum_type_exists = self.in_supp_instrums(param_type)
            if instrum_type_exists:
                instrum_params.append(param)
        if len(instrum_params) == 1:
            return self.sig.rn_param(instrum_params[0], "instrum")
        return None


# pylint: disable=too-few-public-methods
class InferSigInstrumByPosition(InferSigInstrumBase):
    """Infers the `instrum` parameter based on its position in the
    signature.
    """

    def infer(self) -> SensorMethodSignature[Any, Any] | None:
        """Infers the `instrum` parameter based on position.

        Assumes the second param is the instrument, or first param if
        sensor method is static.

        Returns:
            SensorMethodSignature | None: The updated signature if
                inference is successful, otherwise `None`.
        """
        start_pos = 0 if self.sig.sensor.is_static else 1
        params = tuple(self.sig.parameters)
        try:
            param = params[start_pos]
        except IndexError:
            return None
        return self.sig.rn_param(param, "instrum")


class SensorMethodSignature(Signature, Generic[_P, _R]):
    """Represents the `inspect.Signature` of a sensor method with
    extended functionality.

    Provides utilities for parameter inference, renaming, and type
    extraction.

    Args:
        parameters (Sequence[Parameter] | None): The method parameters.
        return_annotation (Any, optional): The return type annotation.
        __validate_parameters__ (bool, optional): Whether to validate
            parameters.
    """

    __slots__: tuple[str, ...] = ("_sensor", "_keys", "_params")

    # Ordered sequence of infer attempts to extract the instrument
    _INFERERS: tuple[type[InferSigInstrumBase], ...] = (
        InferSigInstrumByName,
        InferSigInstrumByAnnotation,
        InferSigInstrumByPosition,
    )

    _sensor: BaseSensorMethod[_P, _R] | None
    _keys: tuple[str, ...] | None
    _params: tuple[Parameter, ...] | None

    def __init__(
        self,
        parameters: Sequence[Parameter] | None = None,
        *,
        return_annotation: Any = None,
        __validate_parameters__: bool = True,
    ) -> None:
        super().__init__(
            parameters,
            return_annotation=return_annotation,
            __validate_parameters__=__validate_parameters__,
        )
        self._sensor = None
        self._keys = None
        self._params = None

    @classmethod
    def from_sensor(
        cls,
        sensor: _SensorMeth,
        *,
        return_annotation: Any = None,
        __validate_parameters__: bool = True,
    ) -> SensorMethodSignature[_P, _R]:
        """Creates a signature instance from a sensor method.

        Args:
            sensor (BaseSensorMethod): The sensor method to analyze.
            return_annotation (Any, optional): The return type
                annotation.
            __validate_parameters__ (bool, optional): Whether to
                validate the parameters, defaults to `True`.

        Returns:
            SensorMethodSignature: The generated signature instance.
        """
        params = tuple(signature(sensor.meth).parameters.values())
        instance = cls(
            params,
            return_annotation=return_annotation,
            __validate_parameters__=__validate_parameters__,
        )
        instance.sensor = sensor
        return instance

    def __len__(self) -> int:
        """Returns the number of parameters in the method signature.

        Returns:
            int: The number of parameters.
        """
        return len(self.parameters)

    @property
    def sensor(self) -> BaseSensorMethod[_P, _R]:
        """Gets the associated sensor method.

        Raises:
            ValueError: If the sensor method is not set during
                initialization.

        Returns:
            BaseSensorMethod: The sensor method associated with the
                signature.
        """
        if self._sensor is None:
            raise ValueError(
                f"{type(self).__name__} not initialized correctly - sensor "
                f"method not set"
            )
        return self._sensor

    @sensor.setter
    def sensor(self, sensor: BaseSensorMethod[_P, _R]) -> None:
        """Sets the sensor method associated with the signature.

        Args:
            sensor (BaseSensorMethod): The sensor method to associate.
        """
        self._sensor = sensor

    @property
    def meth(self) -> Callable[_P, _R]:
        """Retrieves the sensor method.

        Returns:
            Callable[[Any], Any]: The sensor method.
        """
        return self.sensor.meth

    def get_param(self, name: str) -> Parameter:
        """Retrieves a parameter by name.

        Args:
            name (str): The name of the parameter to retrieve.

        Raises:
            ValueError: If the parameter is not found.

        Returns:
            Parameter: The requested parameter object.
        """
        try:
            return next(p for p in self.values if p.name == name)
        except StopIteration as exc:
            raise ValueError(f"Param '{name}' not found in signature") from exc

    def infer(self) -> SensorMethodSignature[Any, Any]:
        """Attempts to infer the `instrum` parameter using available
        inference strategies.

        This method sequentially applies inference techniques to
        try to determine which parameter in the signature represents
        the instrument.

        Returns:
            SensorMethodSignature: A new signature after inference has
                been attempted.
        """
        sig: SensorMethodSignature[_P, _R]
        sig = SensorMethodSignature.from_sensor(self.sensor)
        for inferer_cls in self._INFERERS:
            inferred_sig = inferer_cls(sig).infer()
            if inferred_sig is not None:  # Able to infer
                return inferred_sig
        return sig

    @property
    def keys(self) -> tuple[str, ...]:
        """Gets the names of parameters in the method signature.

        Returns:
            tuple[str, ...]: A tuple of parameter names.
        """
        if self._keys is None:
            self._keys = tuple(self.parameters.keys())
        return self._keys

    @property
    def values(self) -> tuple[Parameter, ...]:
        """Gets the parameters in the method signature.

        Returns:
            tuple[Parameter, ...]: A tuple of parameter objects.
        """
        if self._params is None:
            self._params = tuple(self.parameters.values())
        return self._params

    def replace(
        self,
        *,
        parameters: Sequence[Parameter] | type[Any] | None = None,
        return_annotation: Any = None,
    ) -> Self:
        """Creates a new, modified `SensorMethodSignature` instance.

        Args:
            parameters (Sequence[Parameter] | type[Any] | None, optional):
                The updated parameters for the method signature.
            return_annotation (Any, optional):
                The updated return annotation.

        Returns:
            Self: A new `SensorMethodSignature` instance with the
                updated signature.
        """
        sig = super().replace(
            parameters=parameters, return_annotation=return_annotation
        )
        sig.sensor = self.sensor  # pylint: disable=assigning-non-slot
        return sig

    @overload
    def rn_param(self, param: str, value: str) -> Self: ...

    @overload
    def rn_param(self, param: Parameter, value: str) -> Self: ...

    def rn_param(self, param: str | Parameter, value: str) -> Self:
        """Renames a parameter in the method signature.

        Args:
            param (str | Parameter): The parameter name or object to
                rename.
            value (str): The new name for the parameter.

        Raises:
            ValueError: If the new parameter name already exists.

        Returns:
            Self: A new `SensorMethodSignature` instance with the
                renamed parameter.
        """
        if isinstance(param, str):
            param = self.get_param(param)
        if value in self.keys:
            raise ValueError(f"Cannot rename param - '{value}' already exists")
        renamed_param = param.replace(name=value)
        return self.update_param(old=param, new=renamed_param)

    def update_param(self, *, old: Parameter, new: Parameter) -> Self:
        """Replaces an existing parameter with a new one.

        Args:
            old (Parameter): The parameter to be replaced.
            new (Parameter): The new parameter object.

        Returns:
            Self: A new `SensorMethodSignature` instance with the
                updated parameter.
        """
        params = tuple(new if p == old else p for p in self.values)
        return self.replace(parameters=params)

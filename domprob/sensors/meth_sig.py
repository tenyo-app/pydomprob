from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from inspect import Parameter, Signature, signature
from typing import Any, get_type_hints, overload, TYPE_CHECKING

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if TYPE_CHECKING:
    from domprob.sensors.base_meth import BaseSensorMethod


class InferSigInstrumBase(ABC):

    __slots__: tuple[str, ...] = ("sig",)

    def __init__(self, sig: SensorMethodSignature) -> None:
        self.sig = sig

    @abstractmethod
    def infer(self) -> SensorMethodSignature | None:
        raise NotImplementedError  # pragma: no cover

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(sig={self.sig!r})"


# pylint: disable=too-few-public-methods
class InferSigInstrumByName(InferSigInstrumBase):

    def infer(self) -> SensorMethodSignature | None:
        if "instrum" in self.sig.keys:
            return self.sig
        if "instrument" in self.sig.keys:
            p = self.sig.rn_param("instrument", "instrum")
            return p
        return None


class InferSigInstrumByAnnotation(InferSigInstrumBase):

    __slots__: tuple[str, ...] = ("_supp_instrums", "_type_hints")

    _supp_instrums: tuple[Any, ...] | None
    _type_hints: dict[str, Any] | None

    def __init__(self, sig: SensorMethodSignature) -> None:
        super().__init__(sig)
        self._supp_instrums = None
        self._type_hints = None

    @property
    def supp_instrums(self) -> tuple[Any, ...]:
        if self._supp_instrums is None:
            instrums = tuple(i for i, _ in self.sig.sensor.supp_instrums)
            self._supp_instrums = instrums
        return self._supp_instrums

    @property
    def type_hints(self) -> dict[str, Any]:
        if self._type_hints is None:
            self._type_hints = get_type_hints(self.sig.sensor.meth)
        return self._type_hints

    def in_supp_instrums(self, param_type: Any) -> bool:
        if param_type is None:
            return False
        for instrum in self.supp_instrums:
            if (instrum == param_type) or issubclass(param_type, instrum):
                return True
        return False

    def get_type(self, param: Parameter) -> Any:
        if param.annotation is Parameter.empty:
            return None
        if isinstance(param.annotation, str):
            return self.type_hints.get(param.name)
        return param.annotation

    def infer(self) -> SensorMethodSignature | None:
        instrum_params = []
        if self.sig.sensor.is_static:
            sig_params = self.sig.values
        else:
            sig_params = self.sig.values[1:]
        for param in sig_params:
            param_type = self.get_type(param)
            instrum_type_exists = self.in_supp_instrums(param_type)
            if instrum_type_exists:
                instrum_params.append(param)
        if len(instrum_params) == 1:
            return self.sig.rn_param(instrum_params[0], "instrum")
        return None


# pylint: disable=too-few-public-methods
class InferSigInstrumByPosition(InferSigInstrumBase):

    def infer(self) -> SensorMethodSignature | None:
        start_pos = 0 if self.sig.sensor.is_static else 1
        params = tuple(self.sig.parameters)
        try:
            param = params[start_pos]
        except IndexError:
            return None
        return self.sig.rn_param(param, "instrum")


class SensorMethodSignature(Signature):

    __slots__: tuple[str, ...] = ("_sensor", "_keys", "_params")

    _INFERERS: tuple[type[InferSigInstrumBase], ...] = (
        InferSigInstrumByName,
        InferSigInstrumByAnnotation,
        InferSigInstrumByPosition,
    )

    _sensor: BaseSensorMethod | None
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

    def __len__(self) -> int:
        return len(self.parameters)

    @classmethod
    def from_sensor(
        cls,
        sensor: BaseSensorMethod,
        *,
        return_annotation: Any = None,
        __validate_parameters__: bool = True,
    ) -> SensorMethodSignature:
        params = tuple(signature(sensor.meth).parameters.values())
        instance = cls(
            params,
            return_annotation=return_annotation,
            __validate_parameters__=__validate_parameters__,
        )
        instance.sensor = sensor
        return instance

    @property
    def sensor(self) -> BaseSensorMethod:
        if self._sensor is None:
            raise ValueError(
                f"{type(self).__name__} not initialized correctly - sensor "
                f"method not set"
            )
        return self._sensor

    @sensor.setter
    def sensor(self, sensor: BaseSensorMethod) -> None:
        self._sensor = sensor

    @property
    def meth(self) -> Callable[[Any], Any]:
        return self.sensor.meth

    def get_param(self, name: str) -> Parameter:
        try:
            return next(p for p in self.values if p.name == name)
        except StopIteration as exc:
            raise ValueError(f"Param '{name}' not found in signature") from exc

    def infer(self) -> SensorMethodSignature:
        sig = SensorMethodSignature.from_sensor(self.sensor)
        for inferer_cls in self._INFERERS:
            inferred_sig = inferer_cls(sig).infer()
            if inferred_sig is not None:  # Able to infer
                return inferred_sig
        return sig

    @property
    def keys(self) -> tuple[str, ...]:
        if self._keys is None:
            self._keys = tuple(self.parameters.keys())
        return self._keys

    @property
    def values(self) -> tuple[Parameter, ...]:
        if self._params is None:
            self._params = tuple(self.parameters.values())
        return self._params

    def replace(
        self,
        *,
        parameters: Sequence[Parameter] | type[Any] | None = None,
        return_annotation: Any = None,
    ) -> Self:
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
        if isinstance(param, str):
            param = self.get_param(param)
        if value in self.keys:
            raise ValueError(f"Cannot rename param - '{value}' already exists")
        renamed_param = param.replace(name=value)
        return self.update_param(old=param, new=renamed_param)

    def update_param(self, *, old: Parameter, new: Parameter) -> Self:
        params = tuple(new if p == old else p for p in self.values)
        return self.replace(parameters=params)

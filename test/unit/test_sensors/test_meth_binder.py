import inspect

import pytest

from domprob import sensor
from domprob.sensors.meth import SensorMethod, BoundSensorMethod
from domprob.sensors.meth_binder import (
    PartialBindException,
    SensorMethodBinder,
)


class MockInstrument:
    pass


class AnotherMockInstrument(MockInstrument):
    pass


class YetAnotherMockInstrument(AnotherMockInstrument):
    pass


@pytest.fixture
def mock_cls():
    class Cls:
        def method(self, instrument: MockInstrument) -> None:
            pass

    return Cls


@pytest.fixture
def mock_method(mock_cls):
    return mock_cls.method


class TestPartialBindException:
    def test_exception(self, mock_method):
        # Arrange
        sensor_method = SensorMethod(mock_method)
        exception = TypeError("Some binding error")
        # Act
        result = PartialBindException(sensor_method, exception)
        # Assert
        assert isinstance(result, PartialBindException)
        assert "Failed to bind parameters" in str(result)

    def test_exception_repr(self, mock_method):
        # Arrange
        sensor_method = SensorMethod(mock_method)
        exception = TypeError("Some binding error")
        # Act
        result = repr(PartialBindException(sensor_method, exception))
        # Assert
        assert (
            result == f"PartialBindException(meth={sensor_method!r}, "
            f"e={exception!r})"
        )


class TestSensorMethodBinder:
    def test_initialisation(self, mock_method):
        # Arrange
        sensor_method = SensorMethod(mock_method)
        # Act
        binder = SensorMethodBinder(sensor_method)
        # Assert
        assert binder.sensor_meth == sensor_method

    def test_get_signature_instrument_defined(self, mock_method):
        # Arrange
        sensor_method = SensorMethod(mock_method)
        binder = SensorMethodBinder(sensor_method)
        # Act
        signature = binder.get_signature()
        # Assert
        assert signature == inspect.signature(mock_method)

    def test_get_signature_instrument_defined_in_diff_position(self):
        # Arrange
        class Cls:
            def meth(self, foo: str, instrument: MockInstrument) -> None:
                pass

        sensor_method = SensorMethod(Cls.meth)
        binder = SensorMethodBinder(sensor_method)
        # Act
        signature = binder.get_signature()
        # Assert
        assert signature == inspect.signature(Cls.meth)

    def test_get_signature_infers_instrument_through_annotations(self):
        # Arrange
        class Cls:
            @sensor(MockInstrument)
            @sensor(MockInstrument)
            def meth(self, mock_var_name: MockInstrument) -> None:
                pass

        sensor_method = SensorMethod(Cls.meth)
        binder = SensorMethodBinder(sensor_method)
        # Act
        signature = binder.get_signature()
        # Assert
        assert "instrument" in signature.parameters.keys()
        annotation = signature.parameters.get("instrument").annotation
        assert annotation == MockInstrument
        assert len(signature.parameters) == 2

    def test_get_signature_infers_instrument_through_string_forwarded_annotations(
        self,
    ):
        # Arrange
        class Cls:
            @sensor(MockInstrument)
            @sensor(MockInstrument)
            def meth(self, mock_var_name: "MockInstrument") -> None:
                pass

        sensor_method = SensorMethod(Cls.meth)
        binder = SensorMethodBinder(sensor_method)
        # Act
        signature = binder.get_signature()
        # Assert
        assert "instrument" in signature.parameters.keys()
        annotation = signature.parameters.get("instrument").annotation
        assert annotation == "MockInstrument"
        assert len(signature.parameters) == 2

    def test_get_signature_infers_instrument_through_parent_annotations(self):
        # Arrange
        class Cls:
            @sensor(YetAnotherMockInstrument)
            @sensor(AnotherMockInstrument)
            def meth(self, mock_var_name: MockInstrument) -> None:
                pass

        sensor_method = SensorMethod(Cls.meth)
        binder = SensorMethodBinder(sensor_method)
        # Act
        signature = binder.get_signature()
        # Assert
        assert "instrument" in signature.parameters.keys()
        assert (
            signature.parameters.get("instrument").annotation == MockInstrument
        )
        assert len(signature.parameters) == 2

    def test_get_signature_infers_instrument_through_position_instance_method(
        self,
    ):
        # Arrange
        class Cls:
            def meth(self, mock_var_name) -> None:
                pass

        sensor_method = SensorMethod(Cls.meth)
        binder = SensorMethodBinder(sensor_method)
        # Act
        signature = binder.get_signature()
        # Assert
        assert "instrument" in signature.parameters.keys()
        assert (
            signature.parameters.get("instrument").annotation
            == inspect.Signature.empty
        )
        assert len(signature.parameters) == 2

    def test_get_signature_infers_instrument_through_position_function(self):
        # Arrange
        class Cls:
            @staticmethod
            def meth(mock_var_name) -> None:
                pass

        sensor_method = SensorMethod(Cls.meth)
        binder = SensorMethodBinder(sensor_method)
        # Act
        signature = binder.get_signature()
        # Assert
        assert "instrument" in signature.parameters.keys()
        assert (
            signature.parameters.get("instrument").annotation
            == inspect.Signature.empty
        )
        assert len(signature.parameters) == 1

    @pytest.mark.xfail(
        reason="Checks func type by 'self' variable name convention"
    )
    def test_get_signature_infers_instrument_through_position_when_instance_method_with_incorrect_convention(
        self,
    ):
        # Arrange
        class Cls:
            # noinspection PyMethodParameters
            def meth(uh_oh, mock_var_name) -> None:
                pass

        sensor_method = SensorMethod(Cls.meth)
        binder = SensorMethodBinder(sensor_method)
        # Act
        signature = binder.get_signature()
        # Assert
        assert "uh_oh" in signature.parameters.keys()
        assert "instrument" in signature.parameters.keys()
        assert (
            signature.parameters.get("instrument").annotation
            == inspect.Signature.empty
        )
        assert len(signature.parameters) == 2

    def test_get_signature_infers_instrument_through_position_stop_iteration_function(
        self,
    ):
        # Arrange
        class Cls:
            @staticmethod
            def meth() -> None:
                pass

        sensor_method = SensorMethod(Cls.meth)
        binder = SensorMethodBinder(sensor_method)
        # Act
        signature = binder.get_signature()
        # Assert
        assert signature == inspect.signature(Cls.meth)
        assert len(signature.parameters) == 0

    def test_get_signature_infers_instrument_through_position_stop_iteration_instance_method(
        self,
    ):
        # Arrange
        class Cls:
            def meth(self) -> None:
                pass

        sensor_method = SensorMethod(Cls.meth)
        binder = SensorMethodBinder(sensor_method)
        # Act
        signature = binder.get_signature()
        # Assert
        assert signature == inspect.signature(Cls.meth)
        assert len(signature.parameters) == 1

    def test_bind_self(self, mock_cls, mock_method):
        # Arrange
        sensor_method = SensorMethod(mock_method)
        binder = SensorMethodBinder(sensor_method)
        cls_instance = mock_cls()
        # Act
        bound_method = binder.bind(cls_instance)
        # Assert
        assert isinstance(bound_method, BoundSensorMethod)
        assert bound_method.params.args == (cls_instance,)

    def test_bind_self_and_instrument(self, mock_cls, mock_method):
        # Arrange
        sensor_method = SensorMethod(mock_method)
        binder = SensorMethodBinder(sensor_method)
        cls_instance = mock_cls()
        instrument = MockInstrument()
        # Act
        bound_method = binder.bind(cls_instance, instrument)
        # Assert
        assert isinstance(bound_method, BoundSensorMethod)
        assert bound_method.params.args == (cls_instance, instrument)

    def test_bind_self_and_kw_instrument(self, mock_cls, mock_method):
        # Arrange
        sensor_method = SensorMethod(mock_method)
        binder = SensorMethodBinder(sensor_method)
        cls_instance = mock_cls()
        instrument = MockInstrument()
        # Act
        bound_method = binder.bind(cls_instance, instrument=instrument)
        # Assert
        assert isinstance(bound_method, BoundSensorMethod)
        assert bound_method.params.args == (cls_instance, instrument)

    def test_bind_applies_defaults(self):
        # Arrange
        class Cls:
            def method(self, x: int = 10) -> None:
                pass

        sensor_method = SensorMethod(Cls.method)
        binder = SensorMethodBinder(sensor_method)
        cls_instance = Cls()
        # Act
        bound_method = binder.bind(cls_instance)
        # Assert
        assert isinstance(bound_method, BoundSensorMethod)
        assert bound_method.params.args == (cls_instance, 10)

    def test_bind_does_not_override_explicit_arg_with_default(self):
        # Arrange
        class Cls:
            def method(self, x: int = 10) -> None:
                pass

        sensor_method = SensorMethod(Cls.method)
        binder = SensorMethodBinder(sensor_method)
        cls_instance = Cls()
        # Act
        bound_method = binder.bind(cls_instance, 5)
        # Assert
        assert isinstance(bound_method, BoundSensorMethod)
        assert bound_method.params.args == (cls_instance, 5)

    def test_bind_fails_unexpected_arg(self):
        # Arrange
        class Cls:
            def method(self, x: int = 10) -> None:
                pass

        sensor_method = SensorMethod(Cls.method)
        binder = SensorMethodBinder(sensor_method)
        cls_instance = Cls()
        # Act
        with pytest.raises(PartialBindException) as exc:
            _ = binder.bind(cls_instance, y=5)
        # Assert
        assert str(exc.value) == (
            f"Failed to bind parameters to {Cls.method!r}: got an unexpected "
            f"keyword argument 'y'"
        )

    def test_repr(self, mock_method):
        # Arrange
        sensor_method = SensorMethod(mock_method)
        binder = SensorMethodBinder(sensor_method)
        # Act
        binder_repr = repr(binder)
        # Assert
        expected = f"SensorMethodBinder(sensor_meth={sensor_method!r})"
        assert binder_repr == expected

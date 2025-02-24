import inspect

import pytest

from domprob import sensor
from domprob.sensors.meth import BoundSensorMethod, SensorMethod
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
        bound_method = binder.bind(cls_instance, instrum=instrument)
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

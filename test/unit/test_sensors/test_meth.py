import pytest

from domprob.sensors.instrums import Instruments
from domprob.sensors.meth import BoundSensorMethod, SensorMethod
from domprob.sensors.meth_meta import SensorMetadata


class MockInstrument:
    pass


@pytest.fixture
def mock_cls():
    class Cls:
        def method(self, instrum: MockInstrument) -> None:
            pass

        @staticmethod
        def static_method(instrum: MockInstrument) -> None:
            pass

    return Cls


@pytest.fixture
def mock_method(mock_cls):
    return mock_cls.method


@pytest.fixture
def mock_static_method(mock_cls):
    return mock_cls.static_method


@pytest.fixture
def mock_instruments(mock_method):
    mock_metadata = SensorMetadata(mock_method)
    return Instruments(mock_metadata)


class TestSensorsMethod:
    def test_initialisation(self, mock_method, mock_instruments):
        # Arrange
        # Act
        sensor_method = SensorMethod(mock_method)
        # Assert
        assert sensor_method.meth == mock_method
        assert sensor_method.supp_instrums == mock_instruments

    def test_repr(self, mock_method):
        # Arrange
        sensor_method = SensorMethod(mock_method)
        # Act
        meth_repr = repr(sensor_method)
        # Assert
        assert meth_repr == f"SensorMethod(meth={mock_method!r})"

    def test_bind(self, mock_cls, mock_method):
        # Arrange
        sensor_method = SensorMethod(mock_method)
        mock_instrument = MockInstrument()
        # Act
        bound_method = sensor_method.bind(mock_instrument)
        _ = bound_method.instrum
        # Assert
        assert isinstance(bound_method, BoundSensorMethod)
        assert bound_method.params.args == (mock_instrument,)
        assert bound_method.params.kwargs == {}

    def test_bind_static(self, mock_cls, mock_static_method):
        # Arrange
        sensor_method = SensorMethod(mock_static_method)
        mock_instrument = MockInstrument()
        # Act
        bound_method = sensor_method.bind(mock_instrument)
        _ = bound_method.instrum
        # Assert
        assert isinstance(bound_method, BoundSensorMethod)
        assert bound_method.params.args == (mock_instrument,)
        assert bound_method.params.kwargs == {}

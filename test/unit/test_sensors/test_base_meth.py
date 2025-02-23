import pytest

from domprob.sensors.base_meth import BaseSensorMethod
from domprob.sensors.instrums import Instruments
from domprob.sensors.meth_meta import SensorMetadata
from domprob.sensors.meth_sig import SensorMethodSignature


class MockInstrument:
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


@pytest.fixture
def mock_instruments(mock_method):
    mock_metadata = SensorMetadata(mock_method)
    return Instruments(mock_metadata)


class TestBaseSensorsMethod:
    def test_init(self, mock_method, mock_instruments):
        # Arrange
        # Act
        base = BaseSensorMethod(mock_method)
        # Assert
        assert base._meth == mock_method
        assert base._supp_instrums is None

    def test_init_with_supp_instrums(self, mock_method, mock_instruments):
        # Arrange
        # Act
        base = BaseSensorMethod(mock_method, supp_instrums=mock_instruments)
        # Assert
        assert base._meth == mock_method
        assert base._supp_instrums == mock_instruments

    def test_sig_prop(self, mock_method, mock_instruments):
        # Arrange
        base = BaseSensorMethod(mock_method)
        # Act
        sig = base.sig
        # Assert
        assert isinstance(sig, SensorMethodSignature)
        assert sig.keys == ("self", "instrument")

    def test_meth_prop(self, mock_method, mock_instruments):
        # Arrange
        base = BaseSensorMethod(mock_method)
        # Act
        # Assert
        assert base.meth == mock_method

    def test_supp_instrums_prop_calcs(self, mock_method, mock_instruments):
        # Arrange
        base = BaseSensorMethod(mock_method)
        # Act
        # Assert
        assert base.supp_instrums == mock_instruments

    def test_supp_instrums_prop(self, mock_method, mock_instruments):
        # Arrange
        base = BaseSensorMethod(mock_method, supp_instrums=mock_instruments)
        # Act
        # Assert
        assert base.supp_instrums == mock_instruments

    def test_repr(self, mock_method, mock_instruments):
        # Arrange
        base = BaseSensorMethod(mock_method, supp_instrums=mock_instruments)
        # Act
        base_repr = repr(base)
        # Assert
        assert base_repr.startswith(
            "BaseSensorMethod(meth=<function mock_cls.<locals>.Cls.method at 0x"
        )

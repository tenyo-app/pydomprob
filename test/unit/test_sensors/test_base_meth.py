import pytest

from domprob.sensors.base_meth import BaseSensorMethod
from domprob.sensors.instrums import Instruments
from domprob.sensors.meth_meta import SensorMetadata
from domprob.sensors.meth_sig import SensorMethodSignature


class MockInstrument:
    pass


class Cls:
    def method(self, instrument: MockInstrument) -> None:
        pass

    @staticmethod
    def static_method(instrument: MockInstrument) -> None:
        pass


@pytest.fixture
def mock_cls():
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


class TestBaseSensorMethod:
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

    def test_is_static_prop_inspect_module_dict(self, monkeypatch):
        # Arrange
        class DynamicCls:
            @staticmethod
            def static_meth():
                pass

        mock_mod = type("MockModule", (), {})()
        mock_cls_dict = {
            "DynamicCls": {"static_meth": staticmethod(DynamicCls.static_meth)}
        }
        mock_mod.__dict__["TestBaseSensorMethod"] = {
            "test_is_static_prop_inspect_module_dict": mock_cls_dict
        }

        def mock_getmodule(_):
            return mock_mod

        monkeypatch.setattr(
            "domprob.sensors.base_meth.getmodule", mock_getmodule
        )
        base = BaseSensorMethod(DynamicCls.static_meth)
        # Act
        is_static = base.is_static
        # Assert
        assert is_static, "Method not detected as static"

    def test_is_static_prop_inspect_module_attr(self, mock_static_method):
        # Arrange
        base = BaseSensorMethod(mock_static_method)
        # Act
        is_static = base.is_static
        # Assert
        assert is_static

    def test_is_static_prop_dynamically_created_cls(self):
        # Arrange
        class MockDynamicCls:
            @staticmethod
            def static_meth():
                pass

        base = BaseSensorMethod(MockDynamicCls.static_meth)
        # Act
        is_static = base.is_static
        # Assert
        assert is_static

    def test_is_static_prop_not_static(self, mock_method):
        # Arrange
        base = BaseSensorMethod(mock_method)
        # Act
        is_static = base.is_static
        # Assert
        assert not is_static

    def test_is_static_cannot_deduce(self, monkeypatch):
        # Arrange
        def free_function():  # No enclosing class
            pass

        def mock_getmodule(_):  # Simulate unknown module
            return None

        monkeypatch.setattr("inspect.getmodule", mock_getmodule)
        base = BaseSensorMethod(free_function)
        # Act
        is_static = base.is_static
        # Assert
        assert not is_static

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
            "BaseSensorMethod(meth=<function Cls.method at 0x"
        )

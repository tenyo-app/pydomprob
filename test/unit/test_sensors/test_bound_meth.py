import inspect
from collections import OrderedDict
from inspect import BoundArguments

import pytest

from domprob.sensors.meth import BoundSensorMethod, SensorMethod


class MockInstrument:
    pass


@pytest.fixture
def mock_cls():
    class Cls:
        # noinspection PyUnusedLocal
        # noinspection PyMethodMayBeStatic
        def method(self, instrum: MockInstrument) -> str:
            return "Executed!"

    return Cls


class TestBoundSensorMethod:

    @staticmethod
    def _create_b_meth(meth, *args, **kwargs):
        sensor_method = SensorMethod(meth)
        sig = inspect.signature(meth)
        b_params = BoundArguments(sig, OrderedDict())
        # Bind the arguments correctly
        bound = sig.bind_partial(*args, **kwargs)
        # Assign the correct args and kwargs
        b_params.arguments = bound.arguments
        return BoundSensorMethod(sensor_method, b_params)

    def test_initialisation_arg(self, mock_cls):
        # Arrange
        mock_instrum = MockInstrument()
        mock_instance = mock_cls()
        # Act
        b_meth = self._create_b_meth(
            mock_cls.method, mock_instance, mock_instrum
        )
        # Assert
        assert b_meth.params.args == (mock_instance, mock_instrum)
        assert b_meth.params.kwargs == {}
        assert b_meth.params.arguments == {
            "self": mock_instance,
            "instrum": mock_instrum,
        }

    def test_instrument_property(self, mock_cls):
        # Arrange
        mock_instance = mock_cls()
        mock_instrum = MockInstrument()
        b_meth = self._create_b_meth(
            mock_cls.method, mock_instance, mock_instrum
        )
        # Act
        instrument = b_meth.instrum
        # Assert
        assert instrument is not None
        assert instrument == mock_instrum

    def test_execute(self, mock_cls):
        # Arrange
        mock_instrum = MockInstrument()
        b_meth = self._create_b_meth(mock_cls.method, mock_cls(), mock_instrum)
        # Act
        result = b_meth.execute()
        # Assert
        assert result == "Executed!"

    def test_repr(self, mock_cls):
        # Arrange
        mock_instance = mock_cls()
        mock_instrum = MockInstrument()
        b_meth = self._create_b_meth(
            mock_cls.method, mock_instance, mock_instrum
        )
        # Act
        meth_repr = repr(b_meth)
        # Assert
        expected_repr = (
            f"BoundSensorMethod(sensor_meth={b_meth._sensor_meth!r},"
            f" bound_params={b_meth.params!r})"
        )
        assert meth_repr == expected_repr

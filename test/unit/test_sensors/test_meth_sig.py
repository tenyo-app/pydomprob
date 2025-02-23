from inspect import Parameter, signature
from unittest.mock import Mock, PropertyMock

import pytest

from domprob import sensor
from domprob.sensors.meth import SensorMethod
from domprob.sensors.meth_sig import (
    InferSigInstrumBase,
    InferSigInstrumByAnnotation,
    InferSigInstrumByName,
    InferSigInstrumByPosition,
    SensorMethodSignature,
)


class TestInferSigInstrumBase:

    @pytest.fixture
    def mock_sensor_method(self):
        mock_method = Mock(spec=SensorMethod)
        mock_method.meth = lambda instrum: instrum
        mock_sensor = Mock()
        type(mock_sensor).supp_instrums = PropertyMock(
            return_value=[(int, "int")]
        )
        mock_method.sensor = mock_sensor
        return mock_method

    @pytest.fixture
    def mock_signature(self, mock_sensor_method):
        return SensorMethodSignature.from_sensor(mock_sensor_method)

    @pytest.fixture
    def mock_inferer_cls(self):
        class InferSigInstrumMock(InferSigInstrumBase):
            def infer(self) -> SensorMethodSignature | None:
                pass

        return InferSigInstrumMock

    def test_init(self, mock_inferer_cls, mock_signature):
        # Arrange
        # Act
        inferer = mock_inferer_cls(mock_signature)
        # Assert
        assert inferer.sig == mock_signature

    def test_repr(self, mock_inferer_cls, mock_signature):
        # Arrange
        inferer = mock_inferer_cls(mock_signature)
        # Act
        inferer_repr = repr(inferer)
        # Assert
        assert inferer_repr == f"InferSigInstrumMock(sig={inferer.sig!r})"


class TestInferSigInstrumByName:

    def test_infer_instrum_param_name(self):
        # Arrange
        class MockObservation:
            def meth(self, instrum):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByName(mock_sig)
        # Act
        inferred = inferer.infer()
        # Assert
        assert inferred is not None, "Cannot infer from param names"
        assert inferred.keys == ("self", "instrum")

    def test_infer_instrum_param_name_when_meth_is_static(self):
        # Arrange
        class MockObservation:
            @staticmethod
            def meth(instrum):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByName(mock_sig)
        # Act
        inferred = inferer.infer()
        # Assert
        assert inferred is not None, "Cannot infer from param names"
        assert inferred.keys == ("instrum",)

    def test_infer_instrument_param_name(self):
        # Arrange
        class MockObservation:
            def meth(self, instrument):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByName(mock_sig)
        # Act
        inferred = inferer.infer()
        # Assert
        assert inferred is not None, "Cannot infer from param names"
        assert inferred.keys == ("self", "instrum")

    def test_infer_instrument_param_name_when_meth_is_static(self):
        # Arrange
        class MockObservation:
            @staticmethod
            def meth(instrument):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByName(mock_sig)
        # Act
        inferred = inferer.infer()
        # Assert
        assert inferred is not None, "Cannot infer from param names"
        assert inferred.keys == ("instrum",)

    def test_cannot_infer_unsupported_param_name(self):
        # Arrange
        class MockObservation:
            def meth(self, random_param):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByName(mock_sig)
        # Act
        inferred = inferer.infer()
        # Assert
        assert inferred is None, "Able to infer from param names"

    def test_cannot_infer_unsupported_param_name_when_meth_is_static(self):
        # Arrange
        class MockObservation:
            @staticmethod
            def meth(random_param):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByName(mock_sig)
        # Act
        inferred = inferer.infer()
        # Assert
        assert inferred is None, "Able to infer from param names"

    def test_cannot_infer_no_param_name(self):
        # Arrange
        class MockObservation:
            def meth(self):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByName(mock_sig)
        # Act
        inferred = inferer.infer()
        # Assert
        assert inferred is None, "Able to infer from param names"

    def test_cannot_infer_no_param_name_when_meth_is_static(self):
        # Arrange
        class MockObservation:
            @staticmethod
            def meth():
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByName(mock_sig)
        # Act
        inferred = inferer.infer()
        # Assert
        assert inferred is None, "Able to infer from param names"


class TestInferSigInstrumByAnnotation:

    def test_supp_instrums_prop(self):
        # Arrange
        class MockObservation:
            @sensor(int)
            def meth(self, position):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByAnnotation(mock_sig)
        # Act
        supp_instrums = inferer.supp_instrums
        # Assert
        assert supp_instrums == (int,)

    def test_type_hints_prop(self):
        # Arrange
        class MockObservation:
            def meth(self, position: int):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByAnnotation(mock_sig)
        # Act
        type_hints = inferer.type_hints
        # Assert
        assert type_hints == {"position": int}

    def test_type_hints_prop_none_defined(self):
        # Arrange
        class MockObservation:
            def meth(self, param_):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByAnnotation(mock_sig)
        # Act
        type_hints = inferer.type_hints
        # Assert
        assert type_hints == {}

    def test_not_in_supp_instrums_param_is_none(self):
        # Arrange
        class MockObservation:
            def meth(self, param_):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByAnnotation(mock_sig)
        # Act
        is_supp_instrum = inferer.in_supp_instrums(None)
        # Assert
        assert is_supp_instrum is False

    def test_not_in_supp_instrums_param(self):
        # Arrange
        class MockObservation:
            @sensor(int)
            def meth(self, param_):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByAnnotation(mock_sig)
        # Act
        is_supp_instrum = inferer.in_supp_instrums(str)
        # Assert
        assert is_supp_instrum is False

    def test_in_supp_instrums_param_is_int(self):
        # Arrange
        class MockObservation:
            @sensor(int)
            def meth(self, param_):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByAnnotation(mock_sig)
        # Act
        is_supp_instrum = inferer.in_supp_instrums(int)
        # Assert
        assert is_supp_instrum is True

    def test_get_type_annotation(self):
        # Arrange
        class MockObservation:
            def meth(self, param_: int):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        param = mock_sig.values[1]
        inferer = InferSigInstrumByAnnotation(mock_sig)
        # Act
        type_ = inferer.get_type(param)
        # Assert
        assert type_ == int

    def test_get_type_annotation_future_ref(self):
        # Arrange
        class MockObservation:
            def meth(self, param_: "int"):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        param = mock_sig.values[1]
        inferer = InferSigInstrumByAnnotation(mock_sig)
        # Act
        type_ = inferer.get_type(param)
        # Assert
        assert type_ == int

    def test_get_type_no_annotation(self):
        # Arrange
        class MockObservation:
            def meth(self, param_):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        param = mock_sig.values[0]
        inferer = InferSigInstrumByAnnotation(mock_sig)
        # Act
        type_ = inferer.get_type(param)
        # Assert
        assert type_ is None

    def test_infer_no_annotations(self):
        # Arrange
        class MockObservation:
            def meth(self, param_):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByAnnotation(mock_sig)
        # Act
        inferred = inferer.infer()
        # Assert
        assert inferred is None

    def test_infer_multiple_annotations(self):
        # Arrange
        class MockObservation:
            @sensor(int)
            def meth(self, param_1: int, param_2: int):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByAnnotation(mock_sig)
        # Act
        inferred = inferer.infer()
        # Assert
        assert inferred is None

    def test_infer_multiple_annotations_with_self(self):
        # Arrange
        class MockObservation:
            @sensor(int)
            def meth(self: int, param_1: int):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByAnnotation(mock_sig)
        # Act
        inferred = inferer.infer()
        # Assert
        assert inferred is not None
        assert tuple(inferred.keys) == (
            "self",
            "instrum",
        )

    def test_infer_multiple_annotations_with_static_meth(self):
        # Arrange
        class MockObservation:
            @staticmethod
            @sensor(int)
            def meth(param_1: int, param_2: int):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByAnnotation(mock_sig)
        # Act
        inferred = inferer.infer()
        # Assert
        assert inferred is None

    def test_infer_annotation(self):
        # Arrange
        class MockObservation:
            @sensor(int)
            def meth(self, param_1, param_2: int):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByAnnotation(mock_sig)
        # Act
        inferred = inferer.infer()
        # Assert
        assert inferred is not None
        assert tuple(inferred.keys) == (
            "self",
            "param_1",
            "instrum",
        ), "Can't infer with single valid type"

    def test_infer_annotation_with_static_meth(self):
        # Arrange
        class MockObservation:
            @staticmethod
            @sensor(int)
            def meth(param_1, param_2: int):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByAnnotation(mock_sig)
        # Act
        inferred = inferer.infer()
        # Assert
        assert inferred is not None
        assert tuple(inferred.keys) == ("param_1", "instrum")


class TestInferSigInstrumByPosition:

    def test_infer(self):
        # Arrange
        class MockObservation:
            def meth(self, position):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByPosition(mock_sig)
        # Act
        inferred = inferer.infer()
        # Assert
        assert inferred is not None, "Cannot infer from param position"
        assert tuple(inferred.keys) == ("self", "instrum")

    def test_infer_with_static_meth(self):
        # Arrange
        class MockObservation:
            @staticmethod
            def meth(position):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByPosition(mock_sig)
        # Act
        inferred = inferer.infer()
        # Assert
        assert inferred is not None, "Cannot infer from param position"
        assert tuple(inferred.keys) == ("instrum",)

    def test_cannot_infer(self):
        # Arrange
        class MockObservation:
            def meth(self):
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByPosition(mock_sig)
        # Act
        inferred = inferer.infer()
        # Assert
        assert inferred is None, "Able to infer from param position"

    def test_cannot_infer_with_static_meth(self):
        # Arrange
        class MockObservation:
            @staticmethod
            def meth():
                pass

        meth = SensorMethod(MockObservation.meth)
        mock_sig = SensorMethodSignature.from_sensor(meth)
        inferer = InferSigInstrumByPosition(mock_sig)
        # Act
        inferred = inferer.infer()
        # Assert
        assert inferred is None, "Able to infer from param position"


class TestSensorMethodSignature:

    @pytest.fixture
    def meth(self):
        class MockObservation:
            @sensor(int)
            def meth(self, instrum: int):
                pass

        return MockObservation.meth

    def test_init(self, meth):
        # Arrange
        params = tuple(signature(meth).parameters.values())
        # Act
        sig = SensorMethodSignature(params)
        # Assert
        assert tuple(sig.parameters.values()) == params
        assert sig._sensor is None
        assert sig._keys is None
        assert sig._params is None

    def test_from_sensor(self, meth):
        # Arrange
        sensor_ = SensorMethod(meth)
        # Act
        sig = SensorMethodSignature.from_sensor(sensor_)
        # Assert
        assert sig.sensor is sensor_
        assert sig._keys is None
        assert sig._params is None

    def test_len(self, meth):
        # Arrange
        params = tuple(signature(meth).parameters.values())
        sig = SensorMethodSignature(params)
        # Act
        sig_len = len(sig)
        # Assert
        assert sig_len == 2

    def test_sensor_property_raises(self, meth):
        # Arrange
        params = tuple(signature(meth).parameters.values())
        sig = SensorMethodSignature(params)
        # Act
        with pytest.raises(ValueError) as exc:
            _ = sig.sensor
        # Assert
        assert str(exc.value) == (
            "SensorMethodSignature not initialized correctly - sensor method "
            "not set"
        )

    def test_sensor_property(self, meth):
        # Arrange
        params = tuple(signature(meth).parameters.values())
        sig = SensorMethodSignature(params)
        sensor_ = SensorMethod(meth)
        sig.sensor = sensor_
        # Act
        # Assert
        assert sensor_ == sig.sensor

    def test_meth_prop(self, meth):
        # Arrange
        params = tuple(signature(meth).parameters.values())
        sig = SensorMethodSignature(params)
        sig.sensor = SensorMethod(meth)
        # Act
        # Assert
        assert sig.meth == sig._sensor.meth

    def test_get_param(self, meth):
        # Arrange
        params = tuple(signature(meth).parameters.values())
        sig = SensorMethodSignature(params)
        # Act
        p = sig.get_param("instrum")
        # Assert
        assert p == Parameter(
            "instrum", Parameter.POSITIONAL_OR_KEYWORD, annotation=int
        )

    def test_get_param_raises(self, meth):
        # Arrange
        params = tuple(signature(meth).parameters.values())
        sig = SensorMethodSignature(params)
        # Act
        with pytest.raises(ValueError) as exc:
            _ = sig.get_param("fake_param")
        # Assert
        assert str(exc.value) == "Param 'fake_param' not found in signature"

    def test_infer_with_name(self):
        # Arrange
        class MockObservation:
            @sensor(int)
            def meth(self, param_1: int, instrument):
                pass

        params = tuple(signature(MockObservation.meth).parameters.values())
        sig = SensorMethodSignature(params)
        sig.sensor = SensorMethod(MockObservation.meth)
        # Act
        inferred_sig = sig.infer()
        # Assert
        assert inferred_sig.keys == ("self", "param_1", "instrum")

    def test_infer_with_name_with_static_meth(self):
        # Arrange
        class MockObservation:
            @staticmethod
            @sensor(int)
            def meth(param_1: int, instrument):
                pass

        params = tuple(signature(MockObservation.meth).parameters.values())
        sig = SensorMethodSignature(params)
        sig.sensor = SensorMethod(MockObservation.meth)
        # Act
        inferred_sig = sig.infer()
        # Assert
        assert inferred_sig.keys == ("param_1", "instrum")

    def test_infer_with_annotations(self):
        # Arrange
        class MockObservation:
            @sensor(int)
            def meth(self, param_1, param_2: int):
                pass

        params = tuple(signature(MockObservation.meth).parameters.values())
        sig = SensorMethodSignature(params)
        sig.sensor = SensorMethod(MockObservation.meth)
        # Act
        inferred_sig = sig.infer()
        # Assert
        assert inferred_sig.keys == ("self", "param_1", "instrum")

    def test_infer_with_annotations_with_static_meth(self):
        # Arrange
        class MockObservation:
            @staticmethod
            @sensor(int)
            def meth(param_1, param_2: int):
                pass

        params = tuple(signature(MockObservation.meth).parameters.values())
        sig = SensorMethodSignature(params)
        sig.sensor = SensorMethod(MockObservation.meth)
        # Act
        inferred_sig = sig.infer()
        # Assert
        assert inferred_sig.keys == ("param_1", "instrum")

    def test_infer_with_position(self):
        # Arrange
        class MockObservation:
            @sensor(int)
            def meth(self, param_1, param_2):
                pass

        params = tuple(signature(MockObservation.meth).parameters.values())
        sig = SensorMethodSignature(params)
        sig.sensor = SensorMethod(MockObservation.meth)
        # Act
        inferred_sig = sig.infer()
        # Assert
        assert inferred_sig.keys == ("self", "instrum", "param_2")

    def test_infer_with_position_with_static_meth(self):
        # Arrange
        class MockObservation:
            @staticmethod
            @sensor(int)
            def meth(param_1, param_2):
                pass

        params = tuple(signature(MockObservation.meth).parameters.values())
        sig = SensorMethodSignature(params)
        sig.sensor = SensorMethod(MockObservation.meth)
        # Act
        inferred_sig = sig.infer()
        # Assert
        assert inferred_sig.keys == ("instrum", "param_2")

    def test_infer_returns_diff_sig_instance(self):
        # Arrange
        class MockObservation:
            @sensor(int)
            def meth(self):
                pass

        params = tuple(signature(MockObservation.meth).parameters.values())
        sig = SensorMethodSignature(params)
        sig.sensor = SensorMethod(MockObservation.meth)
        # Act
        inferred_sig = sig.infer()
        # Assert
        assert inferred_sig is not sig

    def test_keys_prop(self, meth):
        # Arrange
        params = tuple(signature(meth).parameters.values())
        sig = SensorMethodSignature(params)
        # Act
        # Assert
        assert sig.keys == tuple(sig.parameters.keys())

    def test_values_prop(self, meth):
        # Arrange
        params = tuple(signature(meth).parameters.values())
        sig = SensorMethodSignature(params)
        # Act
        # Assert
        assert sig.values == tuple(sig.parameters.values())

    def test_replace(self, meth):
        # Arrange
        params = tuple(signature(meth).parameters.values())
        sig = SensorMethodSignature(params)
        sig.sensor = SensorMethod(meth)
        param = Parameter(
            "instrum", Parameter.POSITIONAL_OR_KEYWORD, annotation="str"
        )
        # Act
        replaced_sig = sig.replace(parameters=[param])
        # Assert
        assert len(replaced_sig.parameters) == 1
        assert replaced_sig.values[0] == param
        assert sig.sensor is replaced_sig.sensor

    def test_rn_param_str(self, meth):
        # Arrange
        params = tuple(signature(meth).parameters.values())
        sig = SensorMethodSignature(params)
        sig.sensor = SensorMethod(meth)
        # Act
        renamed_sig = sig.rn_param("instrum", "new_instrum")
        # Assert
        assert "new_instrum" in renamed_sig.keys

    def test_rn_param_parameter(self, meth):
        # Arrange
        params = tuple(signature(meth).parameters.values())
        sig = SensorMethodSignature(params)
        sig.sensor = SensorMethod(meth)
        param = sig.values[1]
        # Act
        renamed_sig = sig.rn_param(param, "new_instrum")
        # Assert
        assert "new_instrum" in renamed_sig.keys

    def test_rn_param_not_exists(self, meth):
        # Arrange
        params = tuple(signature(meth).parameters.values())
        sig = SensorMethodSignature(params)
        sig.sensor = SensorMethod(meth)
        # Act
        with pytest.raises(ValueError) as exc:
            _ = sig.rn_param("self", "instrum")
        # Assert
        assert (
            str(exc.value) == "Cannot rename param - 'instrum' already exists"
        )

    def test_update_params(self, meth):
        # Arrange
        params = tuple(signature(meth).parameters.values())
        sig = SensorMethodSignature(params)
        sig.sensor = SensorMethod(meth)
        old_param = sig.values[1]
        new_param = Parameter("new_instrum", Parameter.POSITIONAL_OR_KEYWORD)
        # Act
        renamed_sig = sig.update_param(old=old_param, new=new_param)
        # Assert
        assert new_param in renamed_sig.values

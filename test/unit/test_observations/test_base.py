import pytest

from domprob.sensors.meth import SensorMethod
from domprob import sensor
from domprob.observations.base import BaseObservation, SensorSet
from domprob.observations.observation import ObservationProtocol


class MockObservation(BaseObservation):

    def __init__(self):
        self.called = False

    @sensor("mock_instrument")  # type: ignore
    def sample_sensor(self, _: str):
        self.called = True
        return "Hello, Observer!"


@pytest.fixture
def observation_cls():
    return MockObservation


class TestSensorSet:

    def test_init(self, observation_cls):
        # Arrange
        meth = SensorMethod(observation_cls.sample_sensor)
        # Act
        sensors = SensorSet(meth, meth)
        # Assert
        assert len(sensors._sensor_methods) == 1
        assert sensors._sensor_methods == {meth}

    def test_from_observation_cls_method(self, observation_cls):
        # Arrange
        # Act
        sensors = SensorSet.from_observation(observation_cls)
        # Assert
        assert len(sensors._sensor_methods) == 1
        (meth,) = sensors._sensor_methods
        assert meth.meth == observation_cls.sample_sensor

    def test_contains(self, observation_cls):
        # Arrange
        meth = SensorMethod(observation_cls.sample_sensor)
        # Act
        sensors = SensorSet(meth, meth)
        # Assert
        assert meth in sensors
        assert "" not in sensors
        assert SensorMethod(lambda: ...) not in sensors

    def test_iter(self, observation_cls):
        # Arrange
        meth = SensorMethod(observation_cls.sample_sensor)
        # Act
        sensor_set = SensorSet(meth, meth)
        # Assert
        assert set(iter(sensor_set)) == {meth, meth}

    def test_len(self, observation_cls):
        # Arrange
        meth = SensorMethod(observation_cls.sample_sensor)
        # Act
        sensors = SensorSet(meth, meth)
        # Assert
        assert len(sensors) == 1

    def test_repr(self, observation_cls):
        # Arrange
        meth = SensorMethod(observation_cls.sample_sensor)
        sensors = SensorSet(meth, meth)
        # Act
        sensors_repr = repr(sensors)
        # Assert
        assert sensors_repr == "SensorSet(num_sensors=1)"


class TestBaseObservation:

    def test_follows_observation_protocol(self, observation_cls):
        # Arrange
        observation = observation_cls()
        # Act
        # Assert
        assert isinstance(observation, BaseObservation)
        assert isinstance(observation, ObservationProtocol)

    def test_sensors_generator(self, observation_cls):
        # Arrange
        # Act
        sensors = list(observation_cls.sensors())
        # Assert
        assert len(sensors) == 1
        assert isinstance(sensors[0], SensorMethod)
        assert sensors[0].meth == observation_cls.sample_sensor

    def test_sensors_caching(self, observation_cls):
        # Arrange
        old_sensor = list(observation_cls.sensors())[0]

        # Act
        def new_sensor():
            return "New sensors"

        observation_cls.new_sensor = new_sensor
        cached_sensors = list(observation_cls.sensors())
        # Assert
        assert len(cached_sensors) == 1
        assert cached_sensors[0] == old_sensor

    def test_len_method(self, observation_cls):
        # Arrange
        # Act
        num_sensors = len(observation_cls())
        # Assert
        assert num_sensors == 1

    def test_repr_method(self, observation_cls):
        # Arrange
        # Act
        obs_repr = repr(observation_cls())
        # Assert
        assert obs_repr == "MockObservation(sensors=1)"

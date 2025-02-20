from domprob import BaseObservation, sensor


class MockObservationOne(BaseObservation):
    pass


class MockObservationTwo(BaseObservation):
    @sensor(...)
    def mock_sensor_one(self): ...

    @sensor(...)
    def mock_sensor_two(self): ...


class MockObservationThree(BaseObservation):
    @sensor(...)
    @sensor(...)
    @sensor(...)
    def mock_sensor_one(self): ...

    @sensor(...)
    def mock_sensor_two(self): ...


class TestBaseObservation:

    def test_no_sensors(self):
        # Arrange
        obs = MockObservationOne()
        # Act
        inst_sensors = list(obs.sensors())
        cls_sensors = list(MockObservationOne.sensors())
        # Assert
        assert len(inst_sensors) == 0
        assert len(cls_sensors) == 0
        assert inst_sensors == cls_sensors
        assert len(obs) == 0

    def test_simple_sensors(self):
        # Arrange
        obs = MockObservationTwo()
        # Act
        inst_sensors = list(obs.sensors())
        cls_sensors = list(MockObservationTwo.sensors())
        # Assert
        assert len(inst_sensors) == 2
        assert len(cls_sensors) == 2
        assert inst_sensors == cls_sensors
        assert len(obs) == 2

    def test_stacked_sensors(self):
        # Arrange
        obs = MockObservationThree()
        # Act
        inst_sensors = list(obs.sensors())
        cls_sensors = list(MockObservationThree.sensors())
        # Assert
        assert len(inst_sensors) == 2
        assert len(cls_sensors) == 2
        assert inst_sensors == cls_sensors
        assert len(obs) == 2

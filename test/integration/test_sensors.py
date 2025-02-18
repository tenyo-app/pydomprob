class TestDecoratorImports:
    def test_sensor_decorator(self):
        # Arrange
        from domprob import sensor as alias_sensor
        from domprob.sensors.dec import sensor

        # Act
        # Assert
        assert alias_sensor is sensor

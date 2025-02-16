class TestConsumerImports:
    def test_basic_consumer_cls(self):
        # Arrange
        from domprob import BasicConsumer as AliasBasicConsumer
        from domprob.consumers.basic import BasicConsumer

        # Act
        # Assert
        assert AliasBasicConsumer is BasicConsumer

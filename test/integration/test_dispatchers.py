class TestDispatcherImports:
    def test_basic_dispatcher_cls(self):
        # Arrange
        from domprob import BasicDispatcher as AliasBasicDispatcher
        from domprob.dispatchers.basic import BasicDispatcher

        # Act
        # Assert
        assert AliasBasicDispatcher is BasicDispatcher

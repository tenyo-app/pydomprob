class TestDispatcherExceptionImports:
    def test_base_dispatcher_exception(self):
        # Arrange
        from domprob.exceptions import (
            DispatcherException as AliasDispatcherException,
        )
        from domprob.dispatchers.dispatcher import DispatcherException

        # Act
        # Assert
        assert AliasDispatcherException is DispatcherException

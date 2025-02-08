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

    def test_req_instrum_exception(self):
        # Arrange
        from domprob.exceptions import (
            ReqInstrumException as AliasReqInstrumException,
        )
        from domprob.dispatchers.basic import ReqInstrumException

        # Act
        # Assert
        assert AliasReqInstrumException is ReqInstrumException

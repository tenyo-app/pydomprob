class TestConsumerExceptionImports:
    def test_base_consumer_exception(self):
        # Arrange
        from domprob.exceptions import (
            ConsumerException as AliasConsumerException,
        )
        from domprob.consumers.consumer import ConsumerException
        # Act
        # Assert
        assert AliasConsumerException is ConsumerException

    def test_req_instrum_exception(self):
        # Arrange
        from domprob.exceptions import (
            ReqInstrumException as AliasReqInstrumException,
        )
        from domprob.consumers.basic import ReqInstrumException
        # Act
        # Assert
        assert AliasReqInstrumException is ReqInstrumException

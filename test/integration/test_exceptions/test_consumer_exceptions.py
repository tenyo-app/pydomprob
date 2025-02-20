class TestConsumerExceptionImports:
    def test_base_consumer_exception(self):
        # Arrange
        from domprob.consumers.consumer import ConsumerException
        from domprob.exceptions import (
            ConsumerException as AliasConsumerException,
        )

        # Act
        # Assert
        assert AliasConsumerException is ConsumerException

    def test_req_instrum_exception(self):
        # Arrange
        from domprob.consumers.basic import ReqInstrumException
        from domprob.exceptions import (
            ReqInstrumException as AliasReqInstrumException,
        )

        # Act
        # Assert
        assert AliasReqInstrumException is ReqInstrumException

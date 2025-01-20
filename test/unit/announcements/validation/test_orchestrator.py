from unittest.mock import MagicMock, patch

import pytest

from domprob.announcements.validation.base_validator import BaseValidator
from domprob.announcements.validation.chain import ValidationChain
from domprob.announcements.validation.orchestrator import (
    AnnouncementValidationOrchestrator,
)
from domprob.announcements.validation.validators import (
    InstrumentParamExistsValidator,
    InstrumentTypeValidator,
)


class TestAnnouncementValidationOrchestrator:
    @pytest.fixture
    def orchestrator(self):
        return AnnouncementValidationOrchestrator()

    def test_default_initialisation(self, orchestrator):
        # Arrange
        # Act
        # Assert
        chain = orchestrator._chain
        assert len(chain._links) == 2
        assert isinstance(chain._links[0], InstrumentParamExistsValidator)
        assert isinstance(chain._links[1], InstrumentTypeValidator)

    def test_custom_initialisation(self):
        # Arrange
        mock_chain = MagicMock(spec=ValidationChain)
        # Act
        orchestrator = AnnouncementValidationOrchestrator(chain=mock_chain)
        # Assert
        assert orchestrator._chain == mock_chain

    def test_register_validators(self, orchestrator):
        # Arrange
        class MockValidator(BaseValidator):
            def validate(self, method):
                pass

        # Act
        orchestrator.register(MockValidator)
        # Assert
        assert len(orchestrator._chain._links) == 3
        assert isinstance(orchestrator._chain._links[2], MockValidator)

    @patch("domprob.announcements.method.BoundAnnouncementMethod")
    def test_validate_chain(self, mock_method):
        # Arrange
        mock_chain = MagicMock(spec=ValidationChain)
        orchestrator = AnnouncementValidationOrchestrator(chain=mock_chain)
        # Act
        orchestrator.validate(mock_method)
        # Assert
        mock_chain.validate_chain.assert_called_once_with(mock_method)

    def test_repr(self, orchestrator):
        # Arrange
        # Act
        repr_output = repr(orchestrator)
        # Assert
        assert "AnnouncementValidationOrchestrator" in repr_output
        assert "ValidationChain" in repr_output

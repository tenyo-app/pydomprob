import copy

import pytest

from domprob.announcements.instruments import Instruments
from domprob.announcements.metadata import AnnouncementMetadata


class MockInstrument:
    pass


class AnotherMockInstrument:
    pass


@pytest.fixture
def mock_method():
    class Cls:
        def method(self):
            pass

    return Cls.method


@pytest.fixture
def mock_metadata(mock_method):
    return AnnouncementMetadata(mock_method)


@pytest.fixture
def mock_instruments(mock_metadata):
    return Instruments(mock_metadata)


@pytest.fixture
def mock_another_instruments():
    class AnotherCls:
        def method(self):
            pass

    metadata = AnnouncementMetadata(AnotherCls.method)
    return Instruments(metadata)


class TestInstruments:
    def test_instruments_initialisation(self, mock_metadata):
        # Arrange
        instruments = Instruments(mock_metadata)
        # Act
        # Assert
        assert instruments._metadata == mock_metadata
        assert len(instruments) == 0

    def test_instruments_iteration(self, mock_instruments, mock_metadata):
        # Arrange
        mock_metadata.add(MockInstrument, required=True)
        mock_metadata.add(AnotherMockInstrument, required=False)
        # Act
        result = list(mock_instruments)
        # Assert
        assert len(result) == 2
        assert result[0] == MockInstrument
        assert result[1] == AnotherMockInstrument

    def test_metadata_eq(self, mock_instruments):
        # Arrange
        instruments1 = copy.deepcopy(mock_instruments)
        instruments2 = copy.deepcopy(mock_instruments)
        # Act
        # Assert
        assert instruments1 == instruments2

    def test_metadata_not_eq(self, mock_instruments, mock_another_instruments):
        # Arrange
        mock_instruments.record(MockInstrument, required=False)
        # Act
        # Assert
        assert mock_instruments != mock_another_instruments

    def test_metadata_not_eq_wrong_type(self, mock_instruments):
        # Arrange
        # Act
        # Assert
        assert mock_instruments != "Not equal"

    def test_instruments_record(self, mock_instruments):
        # Arrange
        # Act
        mock_instruments.record(MockInstrument, required=True)
        mock_instruments.record(AnotherMockInstrument, required=False)
        # Assert
        assert len(mock_instruments) == 2
        all_instruments = list(mock_instruments)
        assert MockInstrument in all_instruments
        assert AnotherMockInstrument in all_instruments

    def test_instruments_req_instruments(self, mock_instruments):
        # Arrange
        mock_instruments.record(MockInstrument, required=True)
        mock_instruments.record(AnotherMockInstrument, required=False)
        # Act
        required = list(mock_instruments.req_instruments)
        # Assert
        assert len(required) == 1
        assert required[0] == MockInstrument

    def test_instruments_non_req_instruments(self, mock_instruments):
        # Arrange
        mock_instruments.record(MockInstrument, required=True)
        mock_instruments.record(AnotherMockInstrument, required=False)
        # Act
        non_required = list(mock_instruments.non_req_instruments)
        # Assert
        assert len(non_required) == 1
        assert non_required[0] == AnotherMockInstrument

    def test_instruments_is_required(self, mock_instruments):
        # Arrange
        mock_instruments.record(MockInstrument, required=True)
        mock_instruments.record(AnotherMockInstrument, required=False)
        # Act + Assert
        assert mock_instruments.is_required(MockInstrument) is True
        assert mock_instruments.is_required(AnotherMockInstrument) is False

    def test_instruments_supported_all(self, mock_instruments):
        # Arrange
        mock_instruments.record(MockInstrument, required=True)
        mock_instruments.record(AnotherMockInstrument, required=False)
        # Act
        all_instruments = list(mock_instruments.supported())
        # Assert
        assert len(all_instruments) == 2
        assert MockInstrument in all_instruments
        assert AnotherMockInstrument in all_instruments

    def test_instruments_supported_required(self, mock_instruments):
        # Arrange
        mock_instruments.record(MockInstrument, required=True)
        mock_instruments.record(AnotherMockInstrument, required=False)
        # Act
        required = list(mock_instruments.supported(required=True))
        # Assert
        assert len(required) == 1
        assert required[0] == MockInstrument

    def test_instruments_supported_non_required(self, mock_instruments):
        # Arrange
        mock_instruments.record(MockInstrument, required=True)
        mock_instruments.record(AnotherMockInstrument, required=False)
        # Act
        non_required = list(mock_instruments.supported(required=False))
        # Assert
        assert len(non_required) == 1
        assert non_required[0] == AnotherMockInstrument

    def test_instruments_from_method(self, mock_method, mock_metadata):
        # Arrange
        # Act
        instruments = Instruments.from_method(mock_method)
        # Assert
        assert isinstance(instruments, Instruments)
        assert repr(instruments) == f"Instruments(metadata={mock_metadata!r})"

    def test_instruments_empty_metadata(self, mock_instruments):
        # Arrange
        # Act
        # Assert
        assert len(mock_instruments) == 0
        assert list(mock_instruments) == []
        assert list(mock_instruments.req_instruments) == []
        assert list(mock_instruments.non_req_instruments) == []
        assert mock_instruments.is_required(MockInstrument) is False

    def test_instruments_duplicate_entries(self, mock_instruments):
        # Arrange
        # Act
        mock_instruments.record(MockInstrument, required=True)
        mock_instruments.record(MockInstrument, required=False)
        # Assert
        assert len(mock_instruments) == 2
        all_instruments = list(mock_instruments)
        assert all_instruments.count(MockInstrument) == 2

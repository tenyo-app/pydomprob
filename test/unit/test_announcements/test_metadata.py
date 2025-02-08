import copy
import random

import pytest

from domprob.announcements.metadata import (
    AnnouncementMetadata,
    AnnouncementMetadataEntry,
)


class MockInstrument:
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
def another_mock_metadata(mock_method):
    class AnotherCls:
        def method(self):
            pass

    return AnnouncementMetadata(AnotherCls.method)


class TestAnnouncementMetadataEntry:
    def test_metadata_item_initialisation(self):
        # Arrange
        # Act
        entry = AnnouncementMetadataEntry(MockInstrument, required=False)
        # Assert
        assert entry.instrument_cls is MockInstrument
        assert entry.required is False

        item_default = AnnouncementMetadataEntry(MockInstrument, True)
        assert item_default.required is True

    def test_metadata_item_repr(self):
        # Arrange
        entry = AnnouncementMetadataEntry(MockInstrument, required=False)
        # Act
        entry_repr = repr(entry)
        # Assert
        assert (
            entry_repr
            == f"AnnouncementMetadataEntry(instrument_cls={MockInstrument!r}, "
            f"required=False)"
        )


class TestAnnouncementMetadata:
    def test_metadata_initialisation(self, mock_method, mock_metadata):
        # Arrange
        # Act
        metadata_len = len(mock_metadata)
        metadata_repr = repr(mock_metadata)
        # Assert
        assert metadata_len == 0
        assert metadata_repr == f"AnnouncementMetadata(method={mock_method!r})"

    def test_add_metadata(self, mock_metadata):
        # Arrange
        # Act
        mock_metadata.add(MockInstrument, required=True)
        # Assert
        assert len(mock_metadata) == 1
        entry = next(iter(mock_metadata))
        assert isinstance(entry, AnnouncementMetadataEntry)
        assert entry.instrument_cls is MockInstrument
        assert entry.required is True

    def test_add_multiple_metadata(self, mock_metadata):
        # Arrange
        # Act
        mock_metadata.add(MockInstrument, required=True)
        mock_metadata.add(MockInstrument, required=False)
        mock_metadata.add(MockInstrument, required=True)
        # Assert
        assert len(mock_metadata) == 3
        assert all(
            [isinstance(e, AnnouncementMetadataEntry) for e in mock_metadata]
        )
        assert all([e.instrument_cls is MockInstrument for e in mock_metadata])
        entry_iter = iter(mock_metadata)
        entry_1 = next(entry_iter)
        entry_2 = next(entry_iter)
        entry_3 = next(entry_iter)
        assert entry_1.required is True
        assert entry_2.required is False
        assert entry_3.required is True

    def test_metadata_iteration(self, mock_metadata):
        # Arrange
        # Act
        mock_metadata.add(MockInstrument, required=True)
        mock_metadata.add(MockInstrument, required=False)
        # Assert
        entries = list(mock_metadata)
        assert len(entries) == 2
        assert isinstance(entries[0], AnnouncementMetadataEntry)
        assert entries[0].instrument_cls is MockInstrument
        assert entries[0].required is True
        assert entries[1].required is False

    def test_empty_metadata_iteration(self, mock_metadata):
        # Arrange
        entries = list(mock_metadata)
        # Act
        entries_len = len(entries)
        # Assert
        assert entries_len == 0

    @pytest.mark.parametrize("num_entries", [0, 1, 2])
    def test_metadata_length(self, mock_metadata, num_entries):
        # Arrange
        for _ in range(num_entries):
            is_required = random.choice([True, False])
            mock_metadata.add(MockInstrument, required=is_required)
        # Act
        metadata_len = len(mock_metadata)
        # Assert
        assert metadata_len == num_entries

    def test_metadata_eq(self, mock_metadata, another_mock_metadata):
        # Arrange
        metadata1 = copy.deepcopy(mock_metadata)
        metadata2 = copy.deepcopy(mock_metadata)
        # Act
        # Assert
        assert metadata1 == metadata2

    def test_metadata_not_eq(self, mock_metadata, another_mock_metadata):
        # Arrange
        mock_metadata.add(MockInstrument, required=False)
        # Act
        # Assert
        assert mock_metadata != another_mock_metadata

    def test_metadata_not_eq_wrong_type(self, mock_metadata):
        # Arrange
        # Act
        # Assert
        assert mock_metadata != "Not equal"

    def test_adding_duplicate_metadata(self, mock_metadata):
        # Arrange
        is_required = random.choice([True, False])
        # Act
        mock_metadata.add(MockInstrument, required=is_required)
        mock_metadata.add(MockInstrument, required=is_required)
        # Assert
        assert len(mock_metadata) == 2

    def test_metadata_repr(self, mock_method, mock_metadata):
        # Arrange
        mock_metadata.add(MockInstrument, required=True)
        # Act
        metadata_repr = repr(mock_metadata)
        # Assert
        assert metadata_repr == f"AnnouncementMetadata(method={mock_method!r})"

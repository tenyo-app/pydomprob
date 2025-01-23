from collections.abc import Callable

import pytest

from domprob import announcement, exceptions
from domprob.announcements.metadata import (
    AnnouncementMetadata,
    AnnouncementMetadataEntry,
)


class MockInstrument:

    def __init__(self, stdout: Callable[[str], None]):
        self.stdout = stdout

    def stdout(self, msg: str) -> None:
        self.stdout(msg)


class AnotherMockInstrument(MockInstrument):
    pass


class YetAnotherMockInstrument(MockInstrument):
    pass


class UnrelatedMockInstrument:
    def stdout(self, msg: str) -> None:
        pass


class TestMetadata:
    def test_metadata_not_set_correctly(self):
        # Arrange
        class Cls:
            def no_method(self, instrument: MockInstrument):
                pass

        metadata: list[AnnouncementMetadataEntry]
        metadata = getattr(
            Cls.no_method, AnnouncementMetadata.METADATA_ATTR, None
        )
        # Act
        # Assert
        assert metadata is None

    def test_metadata_set_correctly(self):
        # Arrange
        class Cls:
            @announcement(MockInstrument)
            def simple_method(self, instrument: MockInstrument) -> None:
                pass

        metadata: list[AnnouncementMetadataEntry]
        metadata = getattr(
            Cls.simple_method, AnnouncementMetadata.METADATA_ATTR
        )
        # Act
        # Assert
        assert len(metadata) == 1
        assert metadata[0].instrument_cls == MockInstrument

    def test_metadata_set_correctly_stacked_method(self):
        # Arrange
        class Cls:
            @announcement(MockInstrument)
            @announcement(MockInstrument)
            @announcement(MockInstrument)
            def stacked_method(self, instrument: MockInstrument) -> None:
                pass

        metadata: list[AnnouncementMetadataEntry]
        metadata = getattr(
            Cls.stacked_method, AnnouncementMetadata.METADATA_ATTR
        )
        # Act
        # Assert
        assert len(metadata) == 3
        assert metadata[0].instrument_cls == MockInstrument
        assert metadata[1].instrument_cls == MockInstrument
        assert metadata[2].instrument_cls == MockInstrument

    def test_metadata_set_correctly_different_stacked_method(self):
        # Arrange
        class Cls:
            @announcement(MockInstrument)
            @announcement(AnotherMockInstrument)
            @announcement(YetAnotherMockInstrument)
            def stacked_differently_method(
                self, instrument: MockInstrument
            ) -> None:
                pass

        metadata: list[AnnouncementMetadataEntry]
        metadata = getattr(
            Cls.stacked_differently_method, AnnouncementMetadata.METADATA_ATTR
        )
        # Act
        # Assert
        assert len(metadata) == 3
        assert metadata[0].instrument_cls == YetAnotherMockInstrument
        assert metadata[1].instrument_cls == AnotherMockInstrument
        assert metadata[2].instrument_cls == MockInstrument


class TestInstrumentTypes:

    def test_instrument_type_inheritance(self):
        # Arrange
        class Cls:
            @announcement(AnotherMockInstrument)
            def method(self, instrument: MockInstrument) -> None:
                instrument.stdout("stdout")

        instance = Cls()
        # Act + Assert
        assert instance.method(AnotherMockInstrument(print)) is None

    def test_instrument_type_inheritance_backwards_raises(self):
        # Arrange
        class Cls:
            @announcement(MockInstrument)
            def method(self, instrument: AnotherMockInstrument) -> None:
                instrument.stdout("stdout")

        instance = Cls()
        # Act
        with pytest.raises(exceptions.InstrumentTypeException):
            instance.method(AnotherMockInstrument(print))
        # Assert

    def test_instrument_type_stacked_multiple_inheritance(self):
        # Arrange
        class Cls:
            @announcement(AnotherMockInstrument)
            @announcement(YetAnotherMockInstrument)
            def method(self, instrument: MockInstrument) -> None:
                instrument.stdout("stdout")

        instance = Cls()
        # Act + Assert
        assert instance.method(YetAnotherMockInstrument(print)) is None
        assert instance.method(AnotherMockInstrument(print)) is None

    def test_instrument_type_stacked_multiple_inheritance_raises(self):
        # Arrange
        class Cls:
            @announcement(AnotherMockInstrument)
            @announcement(YetAnotherMockInstrument)
            def method(self, instrument: MockInstrument) -> None:
                instrument.stdout("stdout")

        instance = Cls()
        instru = MockInstrument(print)
        # Act
        with pytest.raises(exceptions.InstrumentTypeException) as exc_info:
            instance.method(instru)
        # Assert
        assert (
            str(exc_info.value)
            == f"Cls.method(...) expects 'instrument' param to be one of: "
            f"[YetAnotherMockInstrument, AnotherMockInstrument], but got: "
            f"{instru!r}"
        )

    def test_unrelated_instrument_type_raises(self):
        # Arrange
        class Cls:
            @announcement(UnrelatedMockInstrument)
            def method(self, instrument: MockInstrument) -> None:
                instrument.stdout("stdout")

        instance = Cls()
        instru = AnotherMockInstrument(print)
        # Act
        with pytest.raises(exceptions.InstrumentTypeException) as exc_info:
            instance.method(instru)
        # Assert
        assert (
            str(exc_info.value)
            == f"Cls.method(...) expects 'instrument' param to be one of: "
            f"[UnrelatedMockInstrument], but got: {instru!r}"
        )

    def test_unrelated_instrument_type_backwards_raises(self):
        # Arrange
        class Cls:
            @announcement(MockInstrument)
            def method(self, instrument: UnrelatedMockInstrument) -> None:
                instrument.stdout("stdout")

        instance = Cls()
        instru = UnrelatedMockInstrument()
        # Act
        with pytest.raises(exceptions.InstrumentTypeException) as exc_info:
            instance.method(instru)
        # Assert
        assert (
            str(exc_info.value)
            == f"Cls.method(...) expects 'instrument' param to be one of: "
            f"[MockInstrument], but got: {instru!r}"
        )


class TestMissingInstrument:

    def test_missing_instrument_instance_raises(self):
        # Arrange
        class Cls:
            @announcement(MockInstrument)
            def method(self, instrument: MockInstrument) -> None:
                pass

        instance = Cls()
        # Act
        with pytest.raises(TypeError) as exc_info:
            instance.method()
        # Assert
        assert str(exc_info.value).endswith(
            "missing 1 required positional argument: 'instrument'"
        )

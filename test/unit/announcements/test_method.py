import inspect
from collections import OrderedDict
from inspect import BoundArguments
from unittest.mock import MagicMock

import pytest

from domprob import announcement
from domprob.announcements.instruments import Instruments
from domprob.announcements.metadata import AnnouncementMetadata
from domprob.announcements.method import (
    AnnouncementMethod,
    BoundAnnouncementMethod,
    PartialBindException,
    AnnouncementMethodBinder,
)


class MockInstrument:
    pass


class AnotherMockInstrument(MockInstrument):
    pass


class YetAnotherMockInstrument(AnotherMockInstrument):
    pass


@pytest.fixture
def mock_cls():
    class Cls:
        def method(self, instrument: MockInstrument) -> None:
            pass

    return Cls


@pytest.fixture
def mock_method(mock_cls):
    return mock_cls.method


@pytest.fixture
def mock_instruments(mock_method):
    mock_metadata = AnnouncementMetadata(mock_method)
    return Instruments(mock_metadata)


class TestPartialBindException:
    def test_exception(self, mock_method):
        # Arrange
        announcement_method = AnnouncementMethod(mock_method)
        exception = TypeError("Some binding error")
        # Act
        result = PartialBindException(announcement_method, exception)
        # Assert
        assert isinstance(result, PartialBindException)
        assert "Failed to bind parameters" in str(result)

    def test_exception_repr(self, mock_method):
        # Arrange
        announcement_method = AnnouncementMethod(mock_method)
        exception = TypeError("Some binding error")
        # Act
        result = repr(PartialBindException(announcement_method, exception))
        # Assert
        assert (
            result == f"PartialBindException(meth={announcement_method!r}, "
            f"e={exception!r})"
        )


class TestAnnouncementMethodBinder:
    def test_initialisation(self, mock_method):
        # Arrange
        announcement_method = AnnouncementMethod(mock_method)
        # Act
        binder = AnnouncementMethodBinder(announcement_method)
        # Assert
        assert binder.announce_meth == announcement_method

    def test_get_signature_instrument_defined(self, mock_method):
        # Arrange
        announcement_method = AnnouncementMethod(mock_method)
        binder = AnnouncementMethodBinder(announcement_method)
        # Act
        signature = binder.get_signature()
        # Assert
        assert signature == inspect.signature(mock_method)

    def test_get_signature_instrument_defined_in_diff_position(self):
        # Arrange
        class Cls:
            def meth(self, foo: str, instrument: MockInstrument) -> None:
                pass
        announcement_method = AnnouncementMethod(Cls.meth)
        binder = AnnouncementMethodBinder(announcement_method)
        # Act
        signature = binder.get_signature()
        # Assert
        assert signature == inspect.signature(Cls.meth)

    def test_get_signature_infers_instrument_through_annotations(self):
        # Arrange
        class Cls:
            @announcement(MockInstrument)
            @announcement(MockInstrument)
            def meth(self, mock_var_name: MockInstrument) -> None:
                pass
        announcement_method = AnnouncementMethod(Cls.meth)
        binder = AnnouncementMethodBinder(announcement_method)
        # Act
        signature = binder.get_signature()
        # Assert
        assert 'instrument' in signature.parameters.keys()
        assert signature.parameters.get('instrument').annotation == MockInstrument
        assert len(signature.parameters) == 2

    def test_get_signature_infers_instrument_through_parent_annotations(self):
        # Arrange
        class Cls:
            @announcement(YetAnotherMockInstrument)
            @announcement(AnotherMockInstrument)
            def meth(self, mock_var_name: MockInstrument) -> None:
                pass
        announcement_method = AnnouncementMethod(Cls.meth)
        binder = AnnouncementMethodBinder(announcement_method)
        # Act
        signature = binder.get_signature()
        # Assert
        assert 'instrument' in signature.parameters.keys()
        assert signature.parameters.get('instrument').annotation == MockInstrument
        assert len(signature.parameters) == 2

    def test_get_signature_infers_instrument_through_position_instance_method(self):
        # Arrange
        class Cls:
            def meth(self, mock_var_name) -> None:
                pass
        announcement_method = AnnouncementMethod(Cls.meth)
        binder = AnnouncementMethodBinder(announcement_method)
        # Act
        signature = binder.get_signature()
        # Assert
        assert 'instrument' in signature.parameters.keys()
        assert signature.parameters.get('instrument').annotation == inspect.Signature.empty
        assert len(signature.parameters) == 2

    def test_get_signature_infers_instrument_through_position_function(self):
        # Arrange
        class Cls:
            @staticmethod
            def meth(mock_var_name) -> None:
                pass

        announcement_method = AnnouncementMethod(Cls.meth)
        binder = AnnouncementMethodBinder(announcement_method)
        # Act
        signature = binder.get_signature()
        # Assert
        assert 'instrument' in signature.parameters.keys()
        assert signature.parameters.get('instrument').annotation == inspect.Signature.empty
        assert len(signature.parameters) == 1

    @pytest.mark.xfail(reason="Checks func type by 'self' variable name convention")
    def test_get_signature_infers_instrument_through_position_when_instance_method_with_incorrect_convention(self):
        # Arrange
        class Cls:
            def meth(uhoh, mock_var_name) -> None:
                pass

        announcement_method = AnnouncementMethod(Cls.meth)
        binder = AnnouncementMethodBinder(announcement_method)
        # Act
        signature = binder.get_signature()
        # Assert
        assert 'uhoh' in signature.parameters.keys()
        assert 'instrument' in signature.parameters.keys()
        assert signature.parameters.get('instrument').annotation == inspect.Signature.empty
        assert len(signature.parameters) == 2

    def test_get_signature_infers_instrument_through_position_stop_iteration_function(self):
        # Arrange
        class Cls:
            @staticmethod
            def meth() -> None:
                pass

        announcement_method = AnnouncementMethod(Cls.meth)
        binder = AnnouncementMethodBinder(announcement_method)
        # Act
        signature = binder.get_signature()
        # Assert
        assert signature == inspect.signature(Cls.meth)
        assert len(signature.parameters) == 0

    def test_get_signature_infers_instrument_through_position_stop_iteration_instance_method(self):
        # Arrange
        class Cls:
            def meth(self) -> None:
                pass

        announcement_method = AnnouncementMethod(Cls.meth)
        binder = AnnouncementMethodBinder(announcement_method)
        # Act
        signature = binder.get_signature()
        # Assert
        assert signature == inspect.signature(Cls.meth)
        assert len(signature.parameters) == 1

    def test_bind_self(self, mock_cls, mock_method):
        # Arrange
        announcement_method = AnnouncementMethod(mock_method)
        binder = AnnouncementMethodBinder(announcement_method)
        cls_instance = mock_cls()
        # Act
        bound_method = binder.bind(cls_instance)
        # Assert
        assert isinstance(bound_method, BoundAnnouncementMethod)
        assert bound_method.params.args == (cls_instance,)

    def test_bind_self_and_instrument(self, mock_cls, mock_method):
        # Arrange
        announcement_method = AnnouncementMethod(mock_method)
        binder = AnnouncementMethodBinder(announcement_method)
        cls_instance = mock_cls()
        instrument = MockInstrument()
        # Act
        bound_method = binder.bind(cls_instance, instrument)
        # Assert
        assert isinstance(bound_method, BoundAnnouncementMethod)
        assert bound_method.params.args == (cls_instance, instrument)

    def test_bind_self_and_kw_instrument(self, mock_cls, mock_method):
        # Arrange
        announcement_method = AnnouncementMethod(mock_method)
        binder = AnnouncementMethodBinder(announcement_method)
        cls_instance = mock_cls()
        instrument = MockInstrument()
        # Act
        bound_method = binder.bind(cls_instance, instrument=instrument)
        # Assert
        assert isinstance(bound_method, BoundAnnouncementMethod)
        assert bound_method.params.args == (cls_instance, instrument)

    def test_bind_applies_defaults(self):
        # Arrange
        class Cls:
            def method(self, x: int = 10) -> None:
                pass

        announcement_method = AnnouncementMethod(Cls.method)
        binder = AnnouncementMethodBinder(announcement_method)
        cls_instance = Cls()
        # Act
        bound_method = binder.bind(cls_instance)
        # Assert
        assert isinstance(bound_method, BoundAnnouncementMethod)
        assert bound_method.params.args == (cls_instance, 10)

    def test_bind_does_not_override_explicit_arg_with_default(self):
        # Arrange
        class Cls:
            def method(self, x: int = 10) -> None:
                pass

        announcement_method = AnnouncementMethod(Cls.method)
        binder = AnnouncementMethodBinder(announcement_method)
        cls_instance = Cls()
        # Act
        bound_method = binder.bind(cls_instance, 5)
        # Assert
        assert isinstance(bound_method, BoundAnnouncementMethod)
        assert bound_method.params.args == (cls_instance, 5)

    def test_bind_fails_unexpected_arg(self):
        # Arrange
        class Cls:
            def method(self, x: int = 10) -> None:
                pass

        announcement_method = AnnouncementMethod(Cls.method)
        binder = AnnouncementMethodBinder(announcement_method)
        cls_instance = Cls()
        # Act
        with pytest.raises(PartialBindException) as exc:
            _ = binder.bind(cls_instance, y=5)
        # Assert
        assert str(exc.value) == (
            f"Failed to bind parameters to {Cls.method!r}: got an unexpected "
            f"keyword argument 'y'"
        )

    def test_repr(self, mock_method):
        # Arrange
        announcement_method = AnnouncementMethod(mock_method)
        binder = AnnouncementMethodBinder(announcement_method)
        # Act
        binder_repr = repr(binder)
        # Assert
        expected = (
            f"AnnouncementMethodBinder(announce_meth={announcement_method!r})"
        )
        assert binder_repr == expected


class TestAnnouncementMethod:
    def test_initialisation(self, mock_method, mock_instruments):
        # Arrange
        # Act
        announcement_method = AnnouncementMethod(mock_method)
        # Assert
        assert announcement_method.meth == mock_method
        assert announcement_method.supp_instrums == mock_instruments

    def test_repr(self, mock_method):
        # Arrange
        announcement_method = AnnouncementMethod(mock_method)
        # Act
        meth_repr = repr(announcement_method)
        # Assert
        assert meth_repr == f"AnnouncementMethod(meth={mock_method!r})"

    def test_bind(self, mock_cls, mock_method):
        # Arrange
        announcement_method = AnnouncementMethod(mock_method)
        mock_instrument = MockInstrument()
        cls_ = mock_cls()
        # Act
        bound_method = announcement_method.bind(cls_, mock_instrument)
        _ = bound_method.instrument
        # Assert
        assert isinstance(bound_method, BoundAnnouncementMethod)
        assert bound_method.params.args == (cls_, mock_instrument)
        assert bound_method.params.kwargs == {}


class TestBoundAnnouncementMethod:
    @staticmethod
    def _create_b_meth(meth, *args, **kwargs):
        announce_meth = AnnouncementMethod(meth)
        sig = inspect.signature(meth)
        b_params = BoundArguments(sig, OrderedDict())
        # Bind the arguments correctly
        bound = sig.bind_partial(*args, **kwargs)
        # Assign the correct args and kwargs
        b_params.arguments = bound.arguments
        return BoundAnnouncementMethod(announce_meth, b_params)

    def test_initialisation_arg(self, mock_cls):
        # Arrange
        mock_instrum = MockInstrument()
        mock_instance = mock_cls()
        # Act
        b_meth = self._create_b_meth(
            mock_cls.method, mock_instance, mock_instrum
        )
        # Assert
        assert b_meth.params.args == (mock_instance, mock_instrum)
        assert b_meth.params.kwargs == {}
        assert b_meth.params.arguments == {
            "self": mock_instance,
            "instrument": mock_instrum,
        }

    def test_instrument_property(self, mock_cls):
        # Arrange
        mock_instance = mock_cls()
        mock_instrum = MockInstrument()
        b_meth = self._create_b_meth(
            mock_cls.method, mock_instance, mock_instrum
        )
        # Act
        instrument = b_meth.instrument
        # Assert
        assert instrument is not None
        assert instrument == mock_instrum

    def test_execute(self):
        # Arrange
        mock_cls = MagicMock()
        mock_cls.method.return_value = "Executed"
        mock_instrum = MockInstrument()
        b_meth = self._create_b_meth(mock_cls.method, mock_cls(), mock_instrum)
        # Act
        result = b_meth.execute()
        # Assert
        assert result == "Executed"

    def test_repr(self, mock_cls):
        # Arrange
        mock_instance = mock_cls()
        mock_instrum = MockInstrument()
        b_meth = self._create_b_meth(
            mock_cls.method, mock_instance, mock_instrum
        )
        # Act
        meth_repr = repr(b_meth)
        # Assert
        expected_repr = (
            f"BoundAnnouncementMethod(announce_meth={b_meth._announce_meth!r},"
            f" bound_params={b_meth.params!r})"
        )
        assert meth_repr == expected_repr

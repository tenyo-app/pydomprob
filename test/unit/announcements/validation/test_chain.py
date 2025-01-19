import pytest

from domprob.announcements.method import BoundAnnouncementMethod
from domprob.announcements.validation.base_validator import BaseAnnouncementValidator
from domprob.announcements.exceptions import AnnouncementException
from domprob.announcements.validation.chain import ValidationChainException, \
    InvalidLinkException


class TestValidationChainException:

    def test_can_raise(self):
        with pytest.raises(ValidationChainException, match="Text exception"):
            raise ValidationChainException("Text exception")

    def test_inherits_from_announcement_exception(self):
        try:
            raise ValidationChainException()
        except AnnouncementException:
            assert True


@pytest.fixture
def mock_good_chain_link():
    class GoodChainLink(BaseAnnouncementValidator):
        def validate(self, method: BoundAnnouncementMethod):
            super().validate(method)
    return GoodChainLink


@pytest.fixture
def mock_bad_chain_link():
    class BadChainLink:
        def validate(self, method: BoundAnnouncementMethod):
            pass
    return BadChainLink


class TestInvalidLinkException:

    def test_can_raise(self, mock_bad_chain_link, mock_good_chain_link):
        with pytest.raises(
                InvalidLinkException,
                match="Invalid link of type 'BadChainLink', expected type "
                      "'GoodChainLink'"
        ):
            raise InvalidLinkException(mock_bad_chain_link(), mock_good_chain_link)

    def test_inherits_from_validation_chain_exception(self, mock_bad_chain_link, mock_good_chain_link):
        try:
            raise InvalidLinkException(mock_bad_chain_link(), mock_good_chain_link)
        except ValidationChainException:
            assert True
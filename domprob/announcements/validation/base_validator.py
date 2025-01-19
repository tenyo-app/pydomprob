from abc import ABC, abstractmethod
from typing import TypeAlias

from domprob.announcements.exceptions import AnnouncementException
from domprob.announcements.method import BoundAnnouncementMethod

_Validator: TypeAlias = "BaseAnnouncementValidator"


class BaseAnnouncementValidator(ABC):

    def __init__(self, next_validator: _Validator | None = None) -> None:
        self.next_ = next_validator

    @abstractmethod
    def validate(self, meth: BoundAnnouncementMethod) -> None:
        if self.next_:
            return self.next_.validate(meth)
        return None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(next_validator={self.next_})"


class ValidatorException(AnnouncementException):
    """Base exception for validator errors."""

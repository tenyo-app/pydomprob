from abc import ABC, abstractmethod
from typing import Any, Optional, TypeAlias

from domprob.announcements.exceptions import AnnouncementException

_ChainLink: TypeAlias = "BaseValidator"


class ValidatorException(AnnouncementException):
    """Base exception for validator errors."""


class BaseValidator(ABC):
    def __init__(self, next_: Optional[_ChainLink] = None) -> None:
        self.next_ = next_

    @abstractmethod
    def validate(self, meth: Any) -> None:
        if self.next_:
            return self.next_.validate(meth)
        return None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(next_={self.next_!r})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"

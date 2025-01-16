from abc import ABC, abstractmethod
from typing import Any, TypeAlias

_ChainLink: TypeAlias = "BaseValidationChainLink"


class BaseValidationChainLink(ABC):
    def __init__(self, next_: _ChainLink | None = None) -> None:
        self.next_ = next_

    @abstractmethod
    def validate(self, obj: Any) -> None:
        if self.next_:
            return self.next_.validate(obj)
        return None

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(next_link={self.next_!r})"

    def __str__(self) -> str:
        return f"{self.__class__.__name__}"

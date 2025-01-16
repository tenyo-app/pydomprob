from abc import ABC, abstractmethod

from announcements.validation import ResponsibilityChainBuilder
from announcements.validators import (ABCAnnouncementValidator,
                                      InstrumentParamExistsValidator,
                                      InstrumentTypeValidator)


class ABCValidationManager(ABC):

    @property
    @abstractmethod
    def validators(self):
        raise NotImplementedError

    @abstractmethod
    def validate(self) -> None:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class AnnouncementValidationManager(ABCValidationManager):

    # Validators are run at decorated function runtime
    VALIDATORS: tuple[type[ABCAnnouncementValidator], ...] = (
        InstrumentParamExistsValidator,
        InstrumentTypeValidator,
    )

    def __init__(self, bound_method) -> None:
        self.bound_method = bound_method

    @property
    def validators(self) -> ABCAnnouncementValidator:
        builder = ResponsibilityChainBuilder(ABCAnnouncementValidator)
        for validator in self.VALIDATORS:
            builder.add_link(validator())
        return builder.build()

    def validate(self) -> None:
        self.validators.validate(self.bound_method)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(bound_method={self.bound_method!r})"

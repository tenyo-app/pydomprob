from domprob.announcements.method import BoundAnnouncementMethod
from domprob.announcements.validation.base_validator import BaseValidator
from domprob.announcements.validation.chain import ValidationChain
from domprob.announcements.validation.validators import (
    InstrumentParamExistsValidator,
    InstrumentTypeValidator,
)


class AnnouncementValidationOrchestrator:

    DEFAULT_VALIDATORS: tuple[type[BaseValidator], ...] = (
        InstrumentParamExistsValidator,
        InstrumentTypeValidator,
    )

    def __init__(self, chain: ValidationChain | None = None):
        self._chain = chain or ValidationChain(BaseValidator)
        self.register(*self.DEFAULT_VALIDATORS)

    def register(self, *validators: type[BaseValidator]) -> None:
        self._chain.extend((v() for v in validators))

    def validate(self, method: BoundAnnouncementMethod) -> None:
        self._chain.validate_chain(method)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._chain!r})"

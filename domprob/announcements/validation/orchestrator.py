from domprob.announcements.method import BoundAnnouncementMethod
from domprob.announcements.validation.base_validator import \
    BaseAnnouncementValidator
from domprob.announcements.validation.chain import ValidationChain
from domprob.announcements.validation.validators import (
    InstrumentParamExistsValidator, InstrumentTypeValidator)


class AnnouncementValidationOrchestrator:

    DEFAULT_VALIDATORS: tuple[type[BaseAnnouncementValidator], ...] = (
        InstrumentParamExistsValidator,
        InstrumentTypeValidator,
    )

    def __init__(
        self,
        chain: ValidationChain | None = None,
        *validators: type[BaseAnnouncementValidator],
    ):
        self._chain = chain or ValidationChain(BaseAnnouncementValidator)
        self.register(*self.DEFAULT_VALIDATORS, *validators)

    def register(self, *validators: type[BaseAnnouncementValidator]) -> None:
        self._chain.extend((v() for v in validators))

    def validate(self, method: BoundAnnouncementMethod) -> None:
        self._chain.validate_chain(method)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._chain!r})"

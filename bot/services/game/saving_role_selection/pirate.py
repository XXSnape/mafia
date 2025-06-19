from mafia.roles import Instigator, Pirate
from services.game.saving_role_selection.subject_and_object import (
    ChoosingSubjectAndObject,
)
from states.game import UserFsm


class PirateSaver(ChoosingSubjectAndObject):
    key_for_saving_data = "marked"
    message_when_selecting_subject = "Кого должен линчевать на подтверждении {url}, чтобы умереть?"
    message_after_selecting_object = (
        "Если {subject_url} подтвердит линчевание "
        "{object_url}, то он погибнет тоже"
    )
    role = Pirate()
    exclude_user_when_selecting_object = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state_when_selecting_object = (
            UserFsm.PIRATE_CHOOSES_OBJECT
        )

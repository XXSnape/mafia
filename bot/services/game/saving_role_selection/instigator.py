from mafia.roles import Instigator
from services.game.saving_role_selection.subject_and_object import (
    ChoosingSubjectAndObject,
)
from states.game import UserFsm



class InstigatorSaver(ChoosingSubjectAndObject):
    key_for_saving_data = "deceived"
    message_when_selecting_subject = (
        "За кого должен проголосовать {url}?"
    )
    message_after_selecting_object = (
        "Днём {subject_url} проголосует за "
        "{object_url}, если попытается голосовать"
    )
    role = Instigator
    exclude_user_when_selecting_object = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state_when_selecting_object = (
            UserFsm.INSTIGATOR_CHOOSES_OBJECT
        )


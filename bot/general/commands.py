from enum import StrEnum


class GroupCommands(StrEnum):
    registration = "Начать регистрацию"
    game = "Запустить игру"
    extend = "Продлить регистрацию на 30 секунд"
    revoke = "Отменить регистрацию"
    leave = "Удалиться из списка зарегистрировавшихся"
    settings = "Настройки игры"
    statistics = "Статистика и рейтинг"
    subscribe = (
        "Подписаться или отписаться от уведомлений о новой игре"
    )


class PrivateCommands(StrEnum):
    help = "Помощь во всем"
    profile = "Посмотреть свой профиль"
    shop = "Магазин"
    anon = "Анонимная отправка сообщений (работает во время игры)"
    leave = "Выйти из игры (работает во время игры)"

from enum import StrEnum


class BotCommands(StrEnum):
    registration = "Начать регистрацию"
    extend = "Продлить регистрацию на 30 секунд"
    revoke = "Отменить регистрацию"
    my_settings = "Персональные настройки"
    settings = "Настройки игры"
    profile = "Посмотреть свой профиль"
    statistics = "Статистика и рейтинг"

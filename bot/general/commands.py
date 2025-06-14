from enum import StrEnum


class BotCommands(StrEnum):
    registration = "Начать регистрацию"
    game = "Запустить игру"
    extend = "Продлить регистрацию на 30 секунд"
    revoke = "Отменить регистрацию"
    leave = "Выйти из игры"
    my_settings = "Персональные настройки игры"
    settings = "Настройки игры"
    profile = "Посмотреть свой профиль"
    statistics = "Статистика и рейтинг"
    help = "Помощь во всем"
    subscribe = (
        "Подписаться или отписаться от уведомлений о новой игре"
    )

from enum import StrEnum


class GroupCommands(StrEnum):
    registration = "Начать регистрацию"
    game = "Запустить игру"
    extend = "Продлить регистрацию на 30 секунд"
    revoke = "Отменить регистрацию"
    leave = "Выйти из игры"
    settings = "Настройки игры"
    statistics = "Статистика и рейтинг"
    subscribe = (
        "Подписаться или отписаться от уведомлений о новой игре"
    )



class PrivateCommands(StrEnum):
    help = "Помощь во всем"
    profile = "Посмотреть свой профиль"
    shop = "Магазин"
    my_settings = "Персональные настройки игры"

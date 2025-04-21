from database.dao.users import UsersDao
from database.schemas.common import TgIdSchema
from general import settings
from general.collection_of_roles import get_data_with_roles
from general.commands import BotCommands
from general.groupings import Groupings
from general.text import (
    CONFIGURE_GAME_SECTION,
    REQUIRED_PERMISSIONS,
    ROLES_SELECTION,
)
from keyboards.inline.builder import generate_inline_kb
from keyboards.inline.buttons.common import HELP_BTN
from keyboards.inline.callback_factory.help import RoleCbData
from keyboards.inline.keypads.help import (
    HOW_TO_SET_UP_GAME_BTN,
    ROLES_SELECTION_BTN,
    get_roles_kb,
    go_back_to_options_kb,
    help_options_kb,
    to_help_kb,
)
from mafia.roles import Instigator, Warden
from services.base import RouterHelper
from utils.pretty_text import make_build, make_pretty


class BaseRouter(RouterHelper):
    async def greetings_to_user(self):
        await UsersDao(session=self.session).get_user_or_create(
            tg_id=TgIdSchema(tg_id=self.message.from_user.id)
        )
        await self.handle_help()

    async def handle_help(self):
        await self.message.delete()
        text = (
            "🤖Что за бот?\n\n"
            "🎩Это бот-ведущий для игры в Мафию с большим количеством ролей, "
            "предлагающий удобный интерфейс для взаимодействия и общения игроков во время игры!"
        )
        await self.message.answer(
            make_build(text), reply_markup=help_options_kb()
        )

    async def view_roles(self):
        await self.callback.message.delete()
        await self.callback.message.answer(
            text=(
                make_build(
                    f"{make_pretty('ℹ️Базовая информация о ролях:')}\n\n"
                    "🚫 В случае поражения деньги ни за что не начисляются\n\n"
                    "🤔 Роли в основном не могут выбирать себя\n\n"
                    "🪙 За повешения днём выплачиваются деньги\n\n"
                    "🤝 У роли могут быть союзники, которые вступят в основную должность после смерти главаря"
                )
            ),
            reply_markup=get_roles_kb(),
        )

    async def how_to_start_game(self):
        text = (
            f"{make_pretty('🎲Как начать игру?')}\n\n\n"
            "👨‍👩‍👧‍👧Бот работает в группах (и супергруппах), поэтому в первую очередь его нужно добавить в чат.\n"
            "Так как игроков нужно информировать, "
            "временно блокировать выбывших и неиграющих или даже "
            f"живых (подробнее в разделе «{ROLES_SELECTION}»), напоминать о важных моментах, "
            f"боту нужно выдать следующие права:\n\n{REQUIRED_PERMISSIONS}\n\n"
            "Без этого нельзя будет запустить процесс регистрации.\n\n"
            f"©️Если с правами все корректно, нужно ввести команду /{BotCommands.registration.name},"
            " чтобы начать регистрацию. По умолчанию она длится 2 минуты, "
            "потом игра начинается. При необходимости продлить это время, администраторы или "
            f"создатель игры могут ввести /{BotCommands.extend.name} и увеличить время на 30 секунд.\n\n"
            f"🛎️Регистрацию можно отменить, введя команду /{BotCommands.revoke.name}. Максимум регистрация длится 5 минут, "
            "затем игра автоматически начнётся. Игру можно запустить раньше, нажав на соответсвующую "
            "кнопку под сообщением о начале регистрации.\n\n"
            f"🎟️Присоединиться к игре можно нажав на кнопку под этим сообщением, "
            f"а выйти с помощью команды {BotCommands.leave.name}\n\n"
            f"❗️Минимум в игре могут участвовать {settings.mafia.minimum_number_of_players} человека, "
            f"максимум {settings.mafia.maximum_number_of_players}. Если за время регистрации минимальное количество игроков не набралось, "
            "игра не запустится."
        )
        await self.callback.message.edit_text(
            text=make_build(text), reply_markup=to_help_kb()
        )

    async def what_are_bids(self):
        text = (
            f"{make_pretty('🃏Что за ставки?')}\n\n\n"
            "💰Во время регистрации любой игрок, который имеет ненулевой баланс, "
            f"может сделать ставку на разрешенную роль (подробнее в разделе «{CONFIGURE_GAME_SECTION}»).\n\n"
            "🎲Так как заранее неизвестно, сколько игроков будет по итогу в игре, роль, на "
            "которую поставил игрок, может быть не задействована, в таком случае деньги возвращаются.\n\n"
            "✅Если ставка зайдет, и роль будет в игре, игрок получит эту роль, а деньги спишутся.\n\n"
            "😯Также ставки серьёзно влияют на то, какие в принципе роли будут в игре, если порядок ролей "
            f"не определен явно или определен частично (об этом в разделе «{CONFIGURE_GAME_SECTION}»).\n\n"
            "👥Предположим, что играют 6 человек. 5 ролей определены заранее, остался 1 слот. "
            "Если ставок не будет, то роль будет выбрана рандомно, а если ставки есть и они, например, "
            f"такие: за {make_pretty(Instigator.role)} "
            f"максимальная ставка 500, за {make_pretty(Warden.role)} "
            f"600, тогда 6ой ролью будет "
            f"{make_pretty(Warden.role)} (об этих ролях можно почитать в разделе «Роли🎭»).\n\n"
            f"🔥В случае досрочного завершения игры (сбой телеграм, "
            f"расформирование группы во время игры и т.д.) "
            f"деньги за сделанные ставки вернутся в полном объеме."
        )
        await self.callback.message.edit_text(
            text=make_build(text),
            reply_markup=generate_inline_kb(
                data_with_buttons=[
                    ROLES_SELECTION_BTN,
                    HOW_TO_SET_UP_GAME_BTN,
                    HELP_BTN,
                ]
            ),
        )

    async def how_to_play(self):
        text = (
            f"{make_pretty('🎮Как играть?')}\n\n\n"
            "🎬Игра состоит из нескольких этапов:\n\n"
            "🎁1) Знакомство\n\n"
            "Бот присылает в личные сообщения краткую информацию о роли, "
            "знакомит с союзниками при наличии и в некоторых случаях "
            "с сокомандниками по группировке.\n\n"
            "🌃2) Наступление ночи\n\n"
            "Ночью бот присылает игрокам предложение что-то сделать в зависимости от "
            f"особенностей полученной роли. Если роль неактивна ночью, сообщений приходить не "
            f"будет (подробнее в «{ROLES_SELECTION}»).\n\n"
            "👿Проигнорировать это сообщение за игру можно 1 раз. "
            "В случае повторного невыполнения "
            "действия, игрок выбывает из игры до наступления следующей ночи и проигрывает по итогу "
            "вне зависимости от чего-либо.\n\n"
            "📅3) Наступление дня\n\n"
            "После завершения ночных баталий бот подводит итоги, сообщает о погибших и "
            "присылает информацию о важных событиях в группу и личные сообщения игрокам. "
            "Жители в этот период обсуждают прошедшую ночь, всячески пытаются убедить других "
            "участников в своей правоте и невиновности.\n\n"
            "🤝4) Предложение голосовать за игрока, которого можно повесить\n\n"
            "В личные сообщения игрокам приходит опросник, в котором можно выбрать живого "
            "участника игры для дальнейшего повешения. Участие в нем необязательно.\n\n"
            "💀5) Подтверждение о повешении\n\n"
            "Этот этап пропускается, если нет кандидата, набравшего "
            "бОльшее количество голосов "
            "на предыдущем шаге.\n"
            "Если же такой кандидат имеется, в группу бот "
            "скидывает опрос с 2-мя вариантами ответа: "
            "повесить или нет. Если за повешение будет большинство, игрок будет кикнут из игры.\n"
            "Кандидат на повешение не может участвовать в опросе.\n\n"
            "ℹ️Примечания:\n\n"
            "🔚1) Игра заканчивается в тот момент, когда побеждает одна из группировок. "
            f"Подробнее об этом в разделе «{ROLES_SELECTION}».\n\n"
            "️🎙️2) После выбывания из игры ночью, бывший участник может написать последнее "
            "сообщение в личку боту, которое будет переслано в общий чат.\n\n"
            f"🤑3) Игрок может победить, даже если умер днём или ночью "
            f"(подобнее о начислении наград в «{ROLES_SELECTION}»).\n\n"
            f"️💬4) Во время игры коммуницировать прямо в боте могут союзники "
            f"и все члены группировки «{Groupings.criminals.value.name}»"
        )
        await self.callback.message.edit_text(
            text=make_build(text),
            reply_markup=generate_inline_kb(
                data_with_buttons=[ROLES_SELECTION_BTN, HELP_BTN]
            ),
        )

    async def how_to_set_up_game(self):
        text = (
            f"{make_pretty('⚙️Как настроить игру?')}\n\n\n"
            f"Чтобы персонально настроить игру, введите команду /{BotCommands.my_settings.name} "
            f"в личные сообщения боту.\n\n"
            "🛠Виды настроек:\n\n"
            "🗃️1) Порядок ролей\n\n"
            "👥Количество игроков варьируется от игры к игре, поэтому пользователям "
            "предоставляется возможность явно определить, "
            f"какие роли будут при определенном числе участников. "
            f"Если порядок ролей определен для всех игроков (максимум "
            f"{settings.mafia.maximum_number_of_players}), ставки не повлияют на "
            "отбор ролей в игру. Если вообще не определен, дело за ставками и рандомом.\n\n"
            "❗️«Базовые роли» переопределять нельзя, "
            "ведь они должны участвовать в каждой игре. Информация "
            "о них будет отображена сразу при нажатии на кнопку. "
            "Также нельзя определить порядок для ролей, которые ранее были забанены. "
            f"Роль из группировки «{Groupings.criminals.value.name}» может быть "
            f"только на каждой 4ой позиции: 4, 8, 12 и т.д\n\n"
            "❌2) Забаненные роли\n\n"
            "😁Нет обязательств играть сразу со всеми ролями. "
            'Если кто-то хочет поиграть в "самую обыкновенную" мафию '
            "с 4 ролями (мафия, мирный, доктор, комиссар) но с "
            "компанией из 20 человек, такая возможность есть!\n\n"
            "Бот пришлет интерфейс, с помощью которого можно выбрать, "
            "какие роли в игре не смогут участвовать. "
            "Но участие не всех ролей можно ограничить. "
            "Есть так называемые «базовые роли», которые гарантированно будут в любой игре.\n\n"
            "🌉3) Длительность ночи\n\n"
            "Определяется в количестве секунд продолжительность ночи\n\n"
            "📅4) Продолжительность дня\n\n"
            "Определяется в количестве секунд продолжительность дня\n\n\n"
            f"{make_pretty("🔧Как применить свои настройки к конкретной группе?")}\n\n\n"
            "👩‍💼В группе настройки игры могут менять только администраторы, "
            "остальные игроки могут прочитать информацию о них.\n\n"
            "🤖Существуют 2 способа определения настроек для группы:\n\n"
            "1) Применять настройки игры любого ее создателя\n"
            "2) Применять настройки администратора, который "
            "последним выставил этот пункт в настройках группы\n\n"
            f"✅Чтобы посмотреть или изменить конфигурацию, введите "
            f"/{BotCommands.settings.name} в группу. "
            f"После этого бот в личные сообщения пришлет информацию и специфичный интерфейс."
        )
        await self.callback.message.edit_text(
            text=make_build(text),
            reply_markup=to_help_kb(),
        )

    async def how_to_see_statistics(self):
        text = (
            f"{make_pretty('📈Как посмотреть статистику?')}\n\n\n"
            f"🥇1) После ночи бот присылает в личку информацию о действиях, "
            f"которые каким-либо образом повлияли на игру. "
            f"Например, если доктор вылечил игрока,"
            f" которого и не пытались убить, ему об этом не сообщат.\n\n"
            f"👤2) По команде /{BotCommands.profile.name} в личные сообщения "
            f"бот пришлет подробнейшую информацию об игроке, его играх и результатах\n\n"
            f"📊3) По команде /{BotCommands.statistics.name} в сообщения "
            f"группы бот пришлет в общий чат информацию о группе и рейтинге игроков"
        )
        await self.callback.message.edit_text(
            text=make_build(text),
            reply_markup=to_help_kb(),
        )

    @staticmethod
    def join(strings: list[str] | None):
        if strings is None:
            return "Нет"
        return "\n● " + "\n● ".join(strings)

    async def get_details_about_role(
        self, callback_data: RoleCbData
    ):
        current_role = get_data_with_roles(callback_data.role_id)
        description = current_role.role_description
        if current_role.is_alias:
            text = (
                f"Роль является союзной к {make_pretty(current_role.boss_name)}. "
                f"В случае смерти главаря вступает в должность рандомный союзник\n\n"
            )
            if current_role.is_mass_mailing_list:
                text += "Может влиять на выбор ночью"
            else:
                text += "Не может влиять на выбор ночью"
        else:
            text = (
                f"🏆Условие победы: {description.wins_if.capitalize()}\n\n"
                f"💪Особый навык: {(description.skill or "Нет")}\n\n"
                f"💰Платят за: {self.join(description.pay_for)}\n\n"
                f"🚫Ограничения: {self.join(description.limitations)}\n\n"
                f"✨Особенности: {self.join(description.features)}"
            )

        common_text = (
            f"🪪Название: {make_pretty(current_role.role)}\n\n"
            f"🎭Группировка: {make_build(current_role.grouping.value.name)}\n\n"
        )
        purpose_of_grouping = None
        if current_role.grouping in (
            Groupings.criminals,
            Groupings.killer,
        ):
            purpose_of_grouping = (
                "Сделать так, чтобы "
                "представителей группы стало больше "
                "или равно остальным участникам игры"
            )
        elif current_role.grouping == Groupings.civilians:
            purpose_of_grouping = (
                f"Уничтожить группировки {Groupings.criminals.value.name} "
                f"и {Groupings.killer.value.name}"
            )
        if purpose_of_grouping:
            common_text += (
                f"🎯Цель группировки: {purpose_of_grouping}\n\n"
            )

        result_text = common_text + text

        await self.callback.message.delete()
        await self.callback.message.answer_photo(
            photo=current_role.photo,
            caption=make_build(result_text),
            reply_markup=go_back_to_options_kb(),
        )

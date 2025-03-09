from aiogram import Router

router = Router(name=__name__)


# @router.callback_query(
#     UserFsm.MAFIA_ATTACKS, UserActionIndexCbData.filter()
# )
# async def mafia_attacks(
#     callback: CallbackQuery,
#     callback_data: UserActionIndexCbData,
#     state: FSMContext,
#     dispatcher: Dispatcher,
# ):
#     await take_action_and_register_user(
#         callback=callback,
#         callback_data=callback_data,
#         state=state,
#         dispatcher=dispatcher,
#         role=Roles.don.value.alias.role,
#     )


# @router.callback_query(
#     UserFsm.DON_ATTACKS, UserActionIndexCbData.filter()
# )
# async def don_attacks(
#     callback: CallbackQuery,
#     callback_data: UserActionIndexCbData,
#     state: FSMContext,
#     dispatcher: Dispatcher,
# ):
#
#     game_data, user_id = await take_action_and_register_user(
#         callback=callback,
#         callback_data=callback_data,
#         state=state,
#         dispatcher=dispatcher,
#         # role=Roles.don,
#     )
#     game_data["killed_by_don"].append(user_id)

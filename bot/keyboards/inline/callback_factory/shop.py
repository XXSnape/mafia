from aiogram.filters.callback_data import CallbackData
from general.resources import Resources


class ChooseToPurchaseCbData(CallbackData, prefix="purchase"):
    resource: Resources

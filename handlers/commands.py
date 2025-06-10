from aiogram import types
from aiogram.filters import Command
from keyboards.events_keyboards import build_status_keyboard
from storage.user_storage import set_user_status

async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот мероприятий IT52.\n"
        "Используй команду /events для просмотра IT-мероприятий в Нижнем Новгороде"
    )

async def cmd_events(message: types.Message):
    set_user_status(message.from_user.id, "future")
    await message.answer(
        "📅 Выберите тип мероприятий:",
        reply_markup=build_status_keyboard()
    )

def register_commands(dp):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_events, Command("events"))
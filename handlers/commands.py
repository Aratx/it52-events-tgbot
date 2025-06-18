from aiogram import types
from aiogram.filters import Command
from keyboards.events_keyboards import build_status_keyboard
from storage.user_storage import set_user_event_status, set_search_results
from services.search_service import search_events_by_query
from keyboards.search_keyboards import build_search_results_keyboard
from services.datetime_utils import parse_datetime, format_datetime
import logging

logger = logging.getLogger(__name__)

async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот мероприятий IT52.\n"
        "Используй команду /events для просмотра IT-мероприятий в Нижнем Новгороде\n"
        "Используй команду /search для поиска мероприятий по ключевым словам"
    )

async def cmd_events(message: types.Message):
    set_user_event_status(message.from_user.id, "future")
    await message.answer(
        "📅 Выберите тип мероприятий:",
        reply_markup=build_status_keyboard()
    )

async def cmd_search(message: types.Message):
    try:
        query = message.text.split(maxsplit=1)[1].strip()
        if not query:
            await message.answer("🔍 Введите поисковый запрос после команды /search")
            return
            
        search_msg = await message.answer(f"🔍 Ищу мероприятия по запросу: {query}...")
        
        events_data = await search_events_by_query(query)
        
        if not events_data:
            await search_msg.edit_text(f"❌ По запросу '{query}' мероприятий не найдено")
            return
            
        response = f"🔍 Результаты по запросу '{query}':\n\n"
        events_list = []
        
        for event in events_data[:5]:
            attrs = event.get('attributes', {})
            dt = parse_datetime(attrs.get('startedAt'))
            date_str = format_datetime(dt) if dt else "Дата не указана"
            title = attrs.get('title', 'Без названия')[:50]
            
            events_list.append({
                "id": event["id"],
                "title": title,
                "date": date_str
            })
            response += f"• {title}\n  📅 {date_str}\n\n"
        
        set_search_results(message.from_user.id, events_data, query)
        
        keyboard = build_search_results_keyboard(events_list, len(events_data) > 5)
        
        await search_msg.edit_text(
            response,
            reply_markup=keyboard
        )
        
    except IndexError:
        await message.answer("🔍 Введите поисковый запрос после команды /search\nПример: /search python")
    except Exception as e:
        logger.error(f"Search command failed: {e}", exc_info=True)
        await message.answer("⚠️ Произошла ошибка при выполнении поиска")

def register_commands(dp):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_events, Command("events"))
    dp.message.register(cmd_search, Command("search"))
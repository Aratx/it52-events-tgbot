from aiogram import types, F
from services.api_service import fetch_event_details
from services.datetime_utils import format_datetime, parse_datetime
from storage.user_storage import get_search_results
from keyboards.search_keyboards import build_back_to_search_keyboard, build_search_results_keyboard
import logging

logger = logging.getLogger(__name__)

async def show_search_event_details(callback: types.CallbackQuery):
    await callback.answer()
    event_id = callback.data.split("_")[-1]
    
    event_data = await fetch_event_details(event_id)
    if not event_data:
        await callback.message.answer("❌ Ошибка при получении данных о мероприятии")
        return
    
    main_data = event_data.get("data", {})
    attributes = main_data.get("attributes", {})
    
    dt = parse_datetime(attributes.get("startedAt"))
    date_str = format_datetime(dt) if dt else "Дата не указана"
    
    description = attributes.get("description", "")
    short_description = description[:500] + ("..." if len(description) > 500 else "")
    
    event_url = attributes.get("slug", "")
    full_url = f"https://www.it52.info/events/{event_url}" if event_url else ""
    
    included = {item["id"]: item for item in event_data.get("included", [])}
    organizer_id = main_data.get("relationships", {}).get("organizer", {}).get("data", {}).get("id")
    organizer = included.get(organizer_id, {}).get("attributes", {})
    
    participants_count = len(main_data.get("relationships", {}).get("participants", {}).get("data", []))
    
    message_text = (
        f"<b>{attributes.get('title', 'Без названия')}</b>\n\n"
        f"📅 <b>Когда:</b> {date_str}\n"
        f"📍 <b>Где:</b> {attributes.get('place', 'Место не указано')}\n"
        f"👤 <b>Организатор:</b> {organizer.get('nickname', 'Организатор не указан')}\n"
        f"👥 <b>Участники:</b> {participants_count}\n"
        f"🏷️ <b>Теги:</b> {', '.join(attributes.get('tagList', [])) or 'нет тегов'}\n\n"
        f"{short_description}\n\n"
    )
    
    if full_url:
        message_text += f"<a href='{full_url}'>🔗 Подробнее на сайте</a>"
    
    keyboard = build_back_to_search_keyboard()
    
    image_url = attributes.get("titleImage", {}).get("url")
    if image_url:
        await callback.message.answer_photo(
            photo=image_url,
            caption=message_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        await callback.message.answer(
            message_text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=keyboard
        )

async def show_all_search_results(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    search_data = get_search_results(user_id)
    
    if not search_data:
        await callback.message.answer("❌ Результаты поиска устарели")
        return
        
    events_data = search_data.get("results", [])
    query = search_data.get("query", "")
    
    response = f"🔍 Все результаты по запросу '{query}':\n\n"
    for event in events_data:
        attrs = event.get('attributes', {})
        dt = parse_datetime(attrs.get('startedAt'))
        date_str = format_datetime(dt) if dt else "Дата не указана"
        title = attrs.get('title', 'Без названия')[:50]
        
        response += f"• {title}\n  📅 {date_str}\n\n"
        
        if len(response) > 3000:
            response += f"И ещё {len(events_data) - events_data.index(event) - 1} результатов..."
            break
    
    await callback.message.answer(response)

async def back_to_search_results(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    search_data = get_search_results(user_id)
    
    if not search_data:
        await callback.message.answer("❌ Результаты поиска устарели")
        return
        
    events_data = search_data.get("results", [])
    query = search_data.get("query", "")
    
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
    
    keyboard = build_search_results_keyboard(events_list, len(events_data) > 5)
    
    await callback.message.answer(
        response,
        reply_markup=keyboard
    )

def register_search_handlers(dp):
    dp.callback_query.register(show_search_event_details, F.data.startswith("search_event_"))
    dp.callback_query.register(show_all_search_results, F.data == "search_show_all")
    dp.callback_query.register(back_to_search_results, F.data == "back_to_search")
from aiogram import types, F
from services.api_service import get_filtered_events, fetch_event_details
from keyboards.events_keyboards import (
    build_status_keyboard,
    build_back_to_events_keyboard,
    build_events_list_keyboard
)
from storage.user_storage import set_user_event_status, get_user_event_status
from services.datetime_utils import format_datetime, parse_datetime
import logging

logger = logging.getLogger(__name__)

async def handle_status_selection(callback: types.CallbackQuery):
    await callback.answer()
    status = callback.data.split("_")[1]
    user_id = callback.from_user.id
    
    set_user_event_status(user_id, status)
    await callback.message.edit_text("⏳ Загружаю мероприятия...")
    
    events = await get_filtered_events(status)
    
    if not events:
        time_period = "предстоящих" if status == "future" else "прошедших"
        await callback.message.answer(f"❌ Нет доступных {time_period} мероприятий")
        return
    
    await callback.message.answer(
        f"🎉 {'Предстоящие' if status == 'future' else 'Прошедшие'} мероприятия:",
        reply_markup=build_events_list_keyboard(events, status)
    )

async def show_event_details(callback: types.CallbackQuery):
    await callback.answer()
    try:
        parts = callback.data.split("_")
        if len(parts) < 3:
            logger.error(f"Invalid callback data: {callback.data}")
            return
            
        status = parts[1]
        event_id = parts[2]
        
        user_id = callback.from_user.id
        stored_status = get_user_event_status(user_id)
        
        if stored_status and stored_status in ["future", "past"]:
            status = stored_status
        
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
        
        image_url = attributes.get("titleImage", {}).get("url")
        if image_url:
            await callback.message.answer_photo(
                photo=image_url,
                caption=message_text,
                parse_mode="HTML",
                reply_markup=build_back_to_events_keyboard(status)
            )
        else:
            await callback.message.answer(
                message_text,
                parse_mode="HTML",
                disable_web_page_preview=True,
                reply_markup=build_back_to_events_keyboard(status)
            )
            
    except Exception as e:
        logger.error(f"Error in show_event_details: {e}", exc_info=True)
        await callback.message.answer("⚠️ Произошла ошибка при загрузке мероприятия")

async def back_to_events_list(callback: types.CallbackQuery):
    await callback.answer()
    status = callback.data.split("_")[3]
    user_id = callback.from_user.id
    
    set_user_event_status(user_id, status)
    events = await get_filtered_events(status)
    
    if not events:
        time_period = "предстоящих" if status == "future" else "прошедших"
        await callback.message.answer(f"❌ Нет доступных {time_period} мероприятий")
        return
    
    await callback.message.answer(
        f"🎉 {'Предстоящие' if status == 'future' else 'Прошедшие'} мероприятия:",
        reply_markup=build_events_list_keyboard(events, status)
    )

async def back_to_status_selection(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "📅 Выберите тип мероприятий:",
        reply_markup=build_status_keyboard()
    )

def register_events_handlers(dp):
    dp.callback_query.register(handle_status_selection, F.data.startswith("status_"))
    dp.callback_query.register(show_event_details, F.data.startswith("event_"))
    dp.callback_query.register(back_to_events_list, F.data.startswith("back_to_events_"))
    dp.callback_query.register(back_to_status_selection, F.data == "back_to_status")
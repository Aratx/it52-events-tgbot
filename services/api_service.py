import aiohttp
import logging
from datetime import datetime, timezone
from data.constants import API_BASE_URL
from services.datetime_utils import parse_datetime, format_datetime

logger = logging.getLogger(__name__)

async def fetch_events():
    """Получение списка всех мероприятий через API"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_BASE_URL}/events", 
                params={"kind": "all"}
            ) as response:
                if response.status != 200:
                    logger.error(f"API error: {response.status}")
                    return None
                return await response.json()
    except Exception as e:
        logger.error(f"API request failed: {e}")
        return None

async def fetch_event_details(event_id: str):
    """Получение деталей конкретного мероприятия"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_BASE_URL}/events/{event_id}") as response:
                if response.status != 200:
                    logger.error(f"Event details API error: {response.status}")
                    return None
                return await response.json()
    except Exception as e:
        logger.error(f"Event details request failed: {e}")
        return None

async def get_filtered_events(status: str):
    """Получение и фильтрация мероприятий по статусу"""
    data = await fetch_events()
    if not data:
        return []
    
    current_time = datetime.now(timezone.utc)
    events = []
    included = {item["id"]: item for item in data.get("included", [])}
    
    for event in data.get("data", []):
        attributes = event.get("attributes", {})
        dt = parse_datetime(attributes.get("startedAt"))
        
        if not dt:
            continue
            
        is_future = dt > current_time
        if status == "future" and not is_future:
            continue
        if status == "past" and is_future:
            continue
            
        organizer_id = event.get("relationships", {}).get("organizer", {}).get("data", {}).get("id")
        organizer_attrs = included.get(organizer_id, {}).get("attributes", {})
        
        events.append({
            "id": event.get("id"),
            "title": attributes.get("title", "Без названия"),
            "date": format_datetime(dt),
            "dt": dt,
            "place": attributes.get("place", "Место не указано"),
            "organizer": organizer_attrs.get("nickname", "Организатор не указан"),
            "description": attributes.get("description", "Описание отсутствует"),
            "image": attributes.get("titleImage", {}).get("url"),
            "tags": attributes.get("tagList", []),
            "slug": attributes.get("slug", ""),
            "participants_count": len(event.get("relationships", {}).get("participants", {}).get("data", []))
        })
        
    reverse = status == "past"
    return sorted(events, key=lambda x: x["dt"], reverse=reverse)
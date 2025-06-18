import aiohttp
import logging
from services.api_service import API_BASE_URL

logger = logging.getLogger(__name__)

async def search_tags(query: str):
    """Поиск тегов по wildcard/regex шаблону"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{API_BASE_URL}/tags", 
                params={"q": query}
            ) as response:
                if response.status != 200:
                    return []
                data = await response.json()
                return [tag['attributes']['name'] for tag in data.get('data', [])]
    except Exception as e:
        logger.error(f"Tag search failed: {e}")
        return []

async def search_events_by_tags(tags: list):
    """Поиск мероприятий по списку тегов"""
    all_events = []
    seen_ids = set()
    
    try:
        async with aiohttp.ClientSession() as session:
            for tag in tags:
                next_url = f"{API_BASE_URL}/events?tag={tag}&per_page=100"
                while next_url:
                    async with session.get(next_url) as response:
                        if response.status != 200:
                            break
                        data = await response.json()
                        
                        for event in data.get('data', []):
                            if event['id'] not in seen_ids:
                                seen_ids.add(event['id'])
                                all_events.append(event)
                        
                        next_url = data.get('links', {}).get('next')
    except Exception as e:
        logger.error(f"Event search failed: {e}")
    
    return all_events

async def search_events_by_query(query: str):
    """Поиск мероприятий по wildcard/regex запросу"""
    found_tags = await search_tags(query)
    if not found_tags:
        return []
    
    return await search_events_by_tags(found_tags)
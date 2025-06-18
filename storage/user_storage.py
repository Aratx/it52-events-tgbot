# Глобальное хранилище состояний пользователей
user_states = {}

def set_user_event_status(user_id: int, status: str):
    """Устанавливает статус фильтра мероприятий для пользователя"""
    if user_id not in user_states:
        user_states[user_id] = {}
    user_states[user_id]["event_status"] = status

def get_user_event_status(user_id: int) -> str:
    """Возвращает статус фильтра мероприятий для пользователя"""
    return user_states.get(user_id, {}).get("event_status")

def set_search_results(user_id: int, results: list, query: str):
    """Сохраняет результаты поиска для пользователя"""
    if user_id not in user_states:
        user_states[user_id] = {}
    user_states[user_id]["search"] = {
        "results": results,
        "query": query
    }

def get_search_results(user_id: int):
    """Возвращает результаты поиска для пользователя"""
    return user_states.get(user_id, {}).get("search")
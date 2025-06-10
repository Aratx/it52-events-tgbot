# Глобальное хранилище статусов пользователей
user_statuses = {}

def get_user_status(user_id: int):
    return user_statuses.get(user_id, {"status": "future"})

def set_user_status(user_id: int, status: str):
    user_statuses[user_id] = {"status": status}
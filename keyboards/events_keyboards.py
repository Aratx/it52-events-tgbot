from aiogram.utils.keyboard import InlineKeyboardBuilder

def build_status_keyboard():
    """Клавиатура для выбора статуса мероприятий"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔮 Предстоящие", callback_data="status_future")
    builder.button(text="📜 Прошедшие", callback_data="status_past")
    builder.adjust(2)
    return builder.as_markup()

def build_back_to_events_keyboard(status: str):
    """Кнопка для возврата к списку мероприятий"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 К списку мероприятий", callback_data=f"back_to_events_{status}")
    return builder.as_markup()

def build_events_list_keyboard(events: list, status: str):
    """Клавиатура со списком мероприятий"""
    builder = InlineKeyboardBuilder()
    for event in events:
        builder.button(
            text=f"{event['title'][:30]}...", 
            callback_data=f"event_{status}_{event['id']}"
        )
    builder.button(text="◀️ Назад", callback_data="back_to_status")
    builder.adjust(1)
    return builder.as_markup()
from aiogram.utils.keyboard import InlineKeyboardBuilder

def build_search_results_keyboard(events: list, show_all_btn: bool = False):
    """Клавиатура для результатов поиска"""
    builder = InlineKeyboardBuilder()
    
    for event in events:
        builder.button(
            text=f"{event['title']}",
            callback_data=f"search_event_{event['id']}"
        )
    
    if show_all_btn:
        builder.button(text="🔍 Показать все", callback_data="search_show_all")
    
    builder.adjust(1)
    return builder.as_markup()

def build_back_to_search_keyboard():
    """Кнопка для возврата к результатам поиска"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 К результатам поиска", callback_data="back_to_search")
    return builder.as_markup()
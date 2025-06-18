from datetime import datetime, timezone
from data.constants import MONTH_NAMES
import logging

logger = logging.getLogger(__name__)

def parse_datetime(iso_date: str) -> datetime:
    """Преобразование строки даты в объект datetime"""
    if not iso_date:
        return None
        
    try:
        iso_date = iso_date.replace("Z", "+00:00")
        if "." in iso_date:  
            dt = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S.%f%z")
        else:
            dt = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S%z")
        return dt
    except ValueError:
        return None

def format_datetime(dt: datetime) -> str:
    """Форматирование даты в читаемый вид"""
    if not dt:
        return "Дата не указана"
    return f"{dt.day} {MONTH_NAMES[dt.month - 1]}, {dt.strftime('%H:%M')}"
import logging
import asyncio
from aiogram import Bot, Dispatcher
from data.config import BOT_TOKEN
from handlers.commands import register_commands
from handlers.events_handlers import register_events_handlers
from handlers.search_handlers import register_search_handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    register_commands(dp)
    register_events_handlers(dp)
    register_search_handlers(dp)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
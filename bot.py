import asyncio
import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)
from config import BOT_TOKEN
from database import init_db
from handlers.misc import start, help_cmd, tips, menu_router
from handlers.run import build_newrun_handler
from handlers.goal import goal, progress
from handlers.stats import stats, history, chart

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


async def post_init(app):
    await init_db()
    await app.bot.set_my_commands([
        ("start", "Начать / главное меню"),
        ("newrun", "Записать пробежку"),
        ("goal", "Установить месячную цель (км)"),
        ("progress", "Прогресс к цели"),
        ("stats", "Общая статистика"),
        ("history", "Последние 10 пробежек"),
        ("chart", "График за 30 дней"),
        ("tips", "Советы для начинающих"),
        ("help", "Список команд"),
    ])


def main():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(build_newrun_handler())

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("tips", tips))
    app.add_handler(CommandHandler("goal", goal))
    app.add_handler(CommandHandler("progress", progress))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("chart", chart))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            menu_router,
        )
    )

    print("Бот запущен. Ctrl+C для остановки.")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

# tasks/report_tasks.py
import os
import asyncpg
from .celery_app import celery_app
from telegram import Bot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
DB_TABLE_NAME = "tortberi.sales_report"

bot = Bot(token=TELEGRAM_TOKEN)


async def fetch_report(report_key: str):
    pool = await asyncpg.create_pool(DATABASE_URL)
    async with pool.acquire() as con:
        if report_key == "total_sales_today":
            return await con.fetch("SELECT COUNT(*) orders, SUM(\"DishDiscountSumInt\") total FROM tortberi.sales_report WHERE DATE(\"OpenTime\")=CURRENT_DATE")
        # TODO: add other SQL cases here


@celery_app.task
def send_report(chat_id: int, report_key: str):
    import asyncio
    async def inner():
        rows = await fetch_report(report_key)
        text = f"Report {report_key}: {rows}"
        await bot.send_message(chat_id=chat_id, text=text)

    asyncio.run(inner())

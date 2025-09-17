# tasks/scheduler.py
import os
import asyncpg
# from croniter import croniter
from datetime import datetime
from tasks.celery_app import celery_app
from tasks.reports import send_report

DATABASE_URL = os.getenv("DATABASE_URL")

# @celery_app.task
# def check_subscriptions():
#     async def inner():
#         pool = await asyncpg.create_pool(DATABASE_URL)
#         now = datetime.now()
#         async with pool.acquire() as con:
#             rows = await con.fetch("SELECT id, chat_id, report_key, cron_expr FROM subscriptions")
#             for r in rows:
#                 if croniter.match(r["cron_expr"], now):
#                     send_report.delay(r["chat_id"], r["report_key"])
#     import asyncio
#     asyncio.run(inner())

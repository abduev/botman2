import json
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ContextTypes,
)
from telegram import BotCommand
from app.db import execute_query, init_db_pool
from app.queries import QUERIES


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REPORT_MENU = [
    ("today_sales", 'Today sales'),
    ("avg_today_bill", "Average today bill"),
    ("weekly_sales", "Sales for last week"),
    ("top_10_dishes", "Top 10 dishes (30d)"),
]


async def on_startup(application):
    # register persistent menu commands
    await init_db_pool()
    commands = [
        BotCommand("get_report", "Получить отчет"),
        BotCommand("subscribe", "Подписаться на отчет"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Bot commands set")


def reports_keyboard(prefix: str = "report"):
    kb = []
    for key, v in QUERIES.items():
        kb.append([InlineKeyboardButton(v["title"], callback_data=f"{prefix}:{key}")])
    kb.append([InlineKeyboardButton("<- Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(kb)



async def get_report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Choose report to run immediately:",
        reply_markup=reports_keyboard(prefix="report"),
    )


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Subscribe button clicked.\n(🚧 Scheduler not yet implemented)",
        reply_markup=reports_keyboard(prefix="subscribe"),
    )


MAIN_KEYBOARD = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("Получить отчет", callback_data="get_report")],
        [InlineKeyboardButton("Подписаться на отчет", callback_data="subscribe")],
    ]
)


async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use the buttons/menu below 👇", reply_markup=MAIN_KEYBOARD)



async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "get_report":
        await query.edit_message_text(
            "Choose report to run immediately:", reply_markup=reports_keyboard(prefix="report")
        )
        return

    if data == "back_to_main":
        await query.edit_message_text("Back to main:", reply_markup=MAIN_KEYBOARD)
        return


    if data == "subscribe":
        await query.edit_message_text("This button is a subscribe for now.")
        return

    if data and data.startswith("report:"):
        key = data.split("report:", 1)[1]
        report = QUERIES.get(key)
        if not report:
            await query.edit_message_text("Unknown report key")
            return

        await query.edit_message_text(f"Generating *{report['title']}* — please wait...", parse_mode="Markdown")
        try:
            sql_query = report["sql"].strip().replace('```sql', '').replace('```', '').strip()
            logger.info(f'Execute a query: {sql_query}')
            rows = await execute_query(sql_query)
        except Exception as exc:
            logger.exception("DB query failed")
            await query.edit_message_text(f"Failed to run report: {exc}")
            return

        logger.info(f'Result: {rows}')

        # serializable_data = [row._asdict() for row in rows]
        text = format_to_message(rows)

        # Telegram messages have size limits; if too long, we send first chunk
        if len(text) > 3800:
            text = text[:3800] + "\n...truncated"
        await query.edit_message_text(text)
        return


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /start to open the menu.")


# def format_to_message(data):
#     """
#     Convert database response to human-readable text message (values only)
#     """
#     if not data:
#         return "No data found 📭"
#
#     if not isinstance(data, list):
#         data = [data]
#
#     message_lines = []
#
#     for item in data:
#         if isinstance(item, dict):
#             for value in item.values():
#                 # Handle different value types
#                 if value is None:
#                     display_value = "Not specified"
#                 elif value == "":
#                     display_value = "—"
#                 elif isinstance(value, bool):
#                     display_value = "✅" if value else "❌"
#                 elif isinstance(value, (int, float)):
#                     display_value = str(value)
#                 else:
#                     display_value = str(value)
#
#                 message_lines.append(f"• {display_value}")
#
#         message_lines.append("")  # Empty line between records
#
#     # Remove last empty line and join
#     return "\n".join(message_lines).strip()
def format_value(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:.2f}"
    return str(v)


def format_to_message(rows):
    if len(rows) == 0:
        return "Нет данных"
    cols = rows[0].keys()
    header = " | ".join(str(c) for c in cols)
    lines = [header, "-|-".join(["-" * len(str(c)) for c in cols])]
    for r in rows:
        line = " | ".join(format_value(r[c]) for c in cols)
        lines.append(line) if line != '' else None

    return "\n".join(lines)

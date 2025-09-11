import json
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    ContextTypes,
)

from db import execute_query
from .queries import QUERIES


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REPORT_MENU = [
    ("today_sales", 'Today sales'),
    ("avg_today_bill", "Average today bill"),
    ("weekly_sales", "Sales for last week"),
    ("top_10_dishes", "Top 10 dishes (30d)"),
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Get a report", callback_data="open_reports")],
        [InlineKeyboardButton("(placeholder) Other", callback_data="placeholder")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome — choose an action:", reply_markup=reply_markup)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "open_reports":
        kb = [[InlineKeyboardButton(label, callback_data=f"report:{key}")]
              for key, label in REPORT_MENU]
        kb.append([InlineKeyboardButton("Back", callback_data="back_to_main")])
        await query.edit_message_text("Choose a report:", reply_markup=InlineKeyboardMarkup(kb))
        return

    if data == "back_to_main":
        kb = [
            [InlineKeyboardButton("Get a report", callback_data="open_reports")],
            [InlineKeyboardButton("(placeholder) Other", callback_data="placeholder")],
        ]
        await query.edit_message_text("Welcome — choose an action:", reply_markup=InlineKeyboardMarkup(kb))
        return

    if data == "placeholder":
        await query.edit_message_text("This button is a placeholder for now.")
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
            rows = await execute_query(sql_query)
        except Exception as exc:
            logger.exception("DB query failed")
            await query.edit_message_text(f"Failed to run report: {exc}")
            return

        serializable_data = [row._asdict() for row in rows]
        text = format_to_message(serializable_data)

        # Telegram messages have size limits; if too long, we send first chunk
        if len(text) > 3800:
            text = text[:3800] + "\n...truncated"
        await query.edit_message_text(json.dumps(text, indent=2, ensure_ascii=False), parse_mode=None)
        return


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /start to open the menu.")


def format_to_message(data):
    """
    Convert database response to human-readable text message (values only)
    """
    if not data:
        return "No data found 📭"

    if not isinstance(data, list):
        data = [data]

    message_lines = []

    for item in data:
        if isinstance(item, dict):
            for value in item.values():
                # Handle different value types
                if value is None:
                    display_value = "Not specified"
                elif value == "":
                    display_value = "—"
                elif isinstance(value, bool):
                    display_value = "✅" if value else "❌"
                elif isinstance(value, (int, float)):
                    display_value = str(value)
                else:
                    display_value = str(value)

                message_lines.append(f"• {display_value}")

        message_lines.append("")  # Empty line between records

    # Remove last empty line and join
    return "\n".join(message_lines).strip()
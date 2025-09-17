from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler, MessageHandler, filters,
)
from app.bot import on_startup, callback_handler, get_report_command, subscribe_command, text_message_handler
from app.db import on_shutdown
from app.settings import BOT_TOKEN


def main():
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set in environment")

    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )

    application.add_handler(CommandHandler("get_report", get_report_command))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))

    # run polling
    application.run_polling()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Courts Info Service:: Telegram Bot main module.
    Useful info:
        - (.env support) https://github.com/theskumar/python-dotenv

    Created:  Sokolov Sergei, 01.10.2022
    Modified: Dmitrii Gusev, 09.11.2022
"""

import logging
import os

from dotenv import load_dotenv
from telegram import Update, MenuButtonDefault
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from courts.bot import VERSION
from courts.bot.config import bot_config
from courts.bot.conversations import search, start, subscriptions, links, commands
from courts.bot.utils.utilities import get_mysql_conn, form_message_from_db_response

# Enable logging
# todo: implement logger config
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)

# environment file to load (default fallback)
ENV_SETTINGS_FILE = ".env.dev"
# ENV_SETTINGS_FILE = ".env.prod"

# environment variable for environment file name to load
ENV_VAR_FOR_SETTINGS_FILE = "COURTS_BOT_SETTINGS"


async def get_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """shows active subs"""
    query = update.callback_query
    await query.answer()
    account_id = str(query.from_user.id)
    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute(
        "select total_rows, last_load_dttm, min_dt, max_dt from dm_v_court_stats"
    )

    result = cursor.fetchall()
    row = result[0]
    message = (
        f"Последнее обновление: {row[1]}\n"
        f"Слушания от {row[2]} до {row[3]}\n"
        f"Всего записей: {format(row[0], ',d').replace(',', ' ')}\n"
        f"User: {query.from_user.name} ({query.from_user.full_name})"
    )
    cursor.execute(
        """select username 
           from config_telegram_bot_account_link  
           where account_id = %(account_id)s 
        """,
        {"account_id": account_id},
    )
    result = cursor.fetchall()
    if len(result) > 0:
        row = result[0]
        message += f"\nПривязан к аккаунту {row[0]}"
    else:
        message += f"\nЧат не связан с аккаунтом сайта."

    await update.callback_query.message.reply_text(message)
    cursor.close()
    conn.close()
    return "START"


def main():
    """Run the bot."""

    logger.info(f"Starting [Courts Info Service:: Telegram Bot]. Version {VERSION}")

    # Load environment variables from .env_hosting file from the project root dir
    config_file: str = os.getenv(
        ENV_VAR_FOR_SETTINGS_FILE, ""
    )  # try to get config value from env variable
    if not config_file:  # no env variable - fall back to default
        config_file = ENV_SETTINGS_FILE
    logger.debug(f"Using environment config: {config_file}")
    logger.debug(f"Current working dir: {os.getcwd()}")
    load_dotenv(dotenv_path=config_file, verbose=True)

    # debug output for loaded variables
    logger.info(
        f"Loaded environment variables:\n"
        # will raise KeyError if no token
        f"API_TOKEN={'OK' if os.environ['API_TOKEN'] else 'No API Token provided!'}\n"
        f"MYSQL_HOST={os.getenv('MYSQL_HOST', 'Value Doesnt Exist!')}\n"
        f"MYSQL_PORT={os.getenv('MYSQL_PORT', 'Value Doesnt Exist!')}\n"
        f"MYSQL_DB={os.getenv('MYSQL_DB', 'Value Doesnt Exist!')}\n"
        f"MYSQL_USER={os.getenv('MYSQL_USER', 'Value Doesnt Exist!')}\n"
        # will raise KeyError if no password
        f"MYSQL_PASS={'OK' if os.environ['MYSQL_PASS'] else 'No MySql Password provided!'}\n"
    )

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.environ["API_TOKEN"]).build()

    # Register the commands.
    application.add_handler(CommandHandler("version", commands.version))

    # Conversation
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start.start),
            MessageHandler(filters.TEXT, start.start),
        ],
        states={
            "START": [
                CommandHandler("start", start.start),
                CallbackQueryHandler(start.start, pattern="^NEW$"),
                CallbackQueryHandler(search.conv_search, pattern="^SEARCH$"),
                CallbackQueryHandler(subscriptions.conv_subs, pattern="^SUBS$"),
                CallbackQueryHandler(links.conv_links, pattern="^LINKS$"),
                CallbackQueryHandler(get_status, pattern="^STATS$"),
                MessageHandler(filters.TEXT, start.start),
            ],
            "SEARCH": [
                CommandHandler("start", start.start),
                CallbackQueryHandler(start.conv_start, pattern="^START$"),
                MessageHandler(filters.TEXT, search.search),
            ],
            "SUBS": [
                CommandHandler("start", start.start),
                CallbackQueryHandler(start.conv_start, pattern="^START$"),
                CallbackQueryHandler(
                    subscriptions.show_subscriptions, pattern="^SUB_LIST$"
                ),
                CallbackQueryHandler(
                    subscriptions.conv_add_subscription, pattern="^SUB_ADD$"
                ),
                CallbackQueryHandler(
                    subscriptions.conv_remove_subscription, pattern="^SUB_REMOVE$"
                ),
                CallbackQueryHandler(
                    subscriptions.remove_subscription_all, pattern="^SUB_REMOVE_ALL$"
                ),
            ],
            "SUBS_ADD": [
                CommandHandler("start", start.start),
                CallbackQueryHandler(subscriptions.conv_subs, pattern="^SUBS$"),
                MessageHandler(filters.TEXT, subscriptions.add_subscription),
            ],
            "SUBS_REMOVE": [
                CommandHandler("start", start.start),
                CallbackQueryHandler(subscriptions.conv_subs, pattern="^SUBS$"),
                MessageHandler(filters.TEXT, subscriptions.remove_subscription),
            ],
            "LINKS": [
                CommandHandler("start", start.start),
                CallbackQueryHandler(start.conv_start, pattern="^START$"),
                CallbackQueryHandler(links.unlink, pattern="^REMOVE_LINK$"),
                MessageHandler(filters.TEXT, links.link),
            ],
        },
        fallbacks=[CommandHandler("start", start.start)],
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    # schedule notification job
    application.job_queue.run_repeating(
        subscriptions.check_subscriptions, interval=bot_config.JOB_SCHEDULE_INTERVAL
    )

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()

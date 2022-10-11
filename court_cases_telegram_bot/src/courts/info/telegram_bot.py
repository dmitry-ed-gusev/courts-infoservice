#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Courts Info Service:: Telegram Bot main module.
    Useful info:
        - (.env support) https://github.com/theskumar/python-dotenv

    Created:  Sokolov Sergei, 01.10.2022
    Modified: Dmitrii Gusev, 06.10.2022
"""

import os
import pymysql
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from court_cases_telegram_bot.src.courts.info.config import bot_config

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def form_message_from_db_response(row) -> str:
    message = "Суд: " + str(row[0]) + "\nДата заседания: " + row[1].isoformat() + "\nКатегория: " + str(
        row[2]) + "\nПорядковый номер: " + str(row[3]) + "\nНомер дела: " + str(
        row[4]) + "\nВремя слушания: " + str(row[5])
    if row[6] and len(row[6]) > 0:
        message = message + "\nМесто проведения: " + str(row[6])
    if row[7] and len(row[7]) > 0:
        message = message + "\nИнформация по делу: " + str(row[7])
    if row[8] and len(row[8]) > 0:
        message = message + "\nСтадия дела: " + str(row[8])
    if row[9] and len(row[9]) > 0:
        message = message + "\nСудья: " + str(row[9])
    if row[10] and len(row[10]) > 0:
        message = message + "\nРезультат слушания: " + str(row[10])
    if row[11] and len(row[11]) > 0:
        message = message + "\nСудебный акт: " + str(row[11])
    message = message + "\nСсылка на дело: " + str(row[12])
    return message


async def check_subscriptions(context: ContextTypes.DEFAULT_TYPE) -> None:
    """sends notifications for subscriptions"""
    conn = pymysql.connect(host=os.environ["MYSQL_HOST"],
                           port=int(os.environ["MYSQL_PORT"]),
                           user=os.environ["MYSQL_USER"],
                           passwd=os.environ["MYSQL_PASS"],
                           database=os.environ["MYSQL_DB"]
                           )
    cursor = conn.cursor()
    cursor.execute("""select account_id, case_num, last_notification_dttm 
                    from config_telegram_bot_subscriptions""")

    subscriptions = cursor.fetchall()

    if not subscriptions:
        return

    for subscription in subscriptions:
        cursor.execute("""select court, check_date, section_name, order_num, case_num, hearing_time, hearing_place,
                        case_info, stage, judge, hearing_result, decision_link, case_link 
                        from dm_court_cases
                        where lower(case_num) like lower(%(case_num)s)
                        and load_dttm > %(last_check_dttm)s
                        order by check_date desc
                        limit %(limit)s""",
                       {"case_num": str(subscription[1]), "limit": bot_config.OUTPUT_LIMIT,
                        "last_check_dttm": subscription[2]})
        result_1 = cursor.fetchall()
        if result_1:
            for row in result_1:
                message = form_message_from_db_response(row)
                await context.bot.send_message(subscription[0], text=message)
            cursor.execute("""update config_telegram_bot_subscriptions 
                            set last_notification_dttm = now()
                            where account_id = %(account_id)s and case_num = %(case_num)s""",
                           {"case_num": str(subscription[1]), "account_id": str(subscription[0])})
            conn.commit()
    cursor.close()
    conn.close()


async def add_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """adds new subscription"""
    account_id = str(update.message.from_user.id)
    case_num = " ".join(context.args)
    conn = pymysql.connect(host=os.environ["MYSQL_HOST"],
                           port=int(os.environ["MYSQL_PORT"]),
                           user=os.environ["MYSQL_USER"],
                           passwd=os.environ["MYSQL_PASS"],
                           database=os.environ["MYSQL_DB"]
                           )
    cursor = conn.cursor()
    cursor.execute("""insert into config_telegram_bot_subscriptions (account_id, case_num, last_notification_dttm)
            select %(account_id)s, lower(%(case_num)s), now() from dual
            where not exists (select 1 from config_telegram_bot_subscriptions 
                where account_id = %(account_id)s and lower(case_num) = lower(%(case_num)s) limit 1)""",
                   {"case_num": case_num, "account_id": account_id})
    conn.commit()
    await update.effective_message.reply_text(f"Добавлена подписка на дело {case_num}")
    cursor.close()
    conn.close()


async def remove_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """removes subscription"""
    account_id = str(update.message.from_user.id)
    case_num = " ".join(context.args)
    conn = pymysql.connect(host=os.environ["MYSQL_HOST"],
                           port=int(os.environ["MYSQL_PORT"]),
                           user=os.environ["MYSQL_USER"],
                           passwd=os.environ["MYSQL_PASS"],
                           database=os.environ["MYSQL_DB"]
                           )
    cursor = conn.cursor()
    if case_num == "all":
        cursor.execute("""delete from config_telegram_bot_subscriptions 
                            where account_id = %(account_id)s""",
                       {"account_id": account_id})
        conn.commit()
        await update.effective_message.reply_text(f"Все подписки удалены. Вы больше не будете получать уведомлений.")
    else:
        cursor.execute("""delete from config_telegram_bot_subscriptions 
                    where account_id = %(account_id)s and lower(case_num) = lower(%(case_num)s)""",
                       {"case_num": case_num, "account_id": account_id})
        conn.commit()
        await update.effective_message.reply_text(f"Удалена подписка на дело {case_num}")
    cursor.close()
    conn.close()


async def get_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """shows active subs"""
    conn = pymysql.connect(host=os.environ["MYSQL_HOST"],
                           port=int(os.environ["MYSQL_PORT"]),
                           user=os.environ["MYSQL_USER"],
                           passwd=os.environ["MYSQL_PASS"],
                           database=os.environ["MYSQL_DB"]
                           )
    cursor = conn.cursor()
    cursor.execute("""select count(*) as total_rows, 
	                date_format(max(load_dttm),'%d.%m.%Y %H:%i') as last_load_dttm, 
	                date_format(min(check_date),'%d.%m.%Y') as min_dt, 
	                date_format(max(check_date),'%d.%m.%Y') as max_dt
                    from dm_court_cases""")

    result = cursor.fetchall()
    message = ""
    for row in result:
        message = "Последнее обновление: " + row[1] + "\nСлушания от " + row[2] + " до " + row[
            3] + ".\nВсего записей: " + str(row[0]) + "."

    await update.effective_message.reply_text(message)
    cursor.close()
    conn.close()


async def show_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """shows active subs"""
    account_id = str(update.message.from_user.id)
    conn = pymysql.connect(host=os.environ["MYSQL_HOST"],
                           port=int(os.environ["MYSQL_PORT"]),
                           user=os.environ["MYSQL_USER"],
                           passwd=os.environ["MYSQL_PASS"],
                           database=os.environ["MYSQL_DB"]
                           )
    cursor = conn.cursor()
    cursor.execute("""select case_num from config_telegram_bot_subscriptions 
                where account_id = %(account_id)s""",
                   {"account_id": account_id})

    result = cursor.fetchall()

    if not result:
        message = "Подписок нет."
        await update.effective_message.reply_text(message)
        return
    message = "Вы подписаны на:\n"
    for row in result:
        message = message + str(row[0]) + "\n"
    message.rstrip("\n")
    await update.effective_message.reply_text(message)
    cursor.close()
    conn.close()


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """searches for court case"""

    # args should contain the case number
    case_num = " ".join(context.args)
    conn = pymysql.connect(host=os.environ["MYSQL_HOST"],
                           port=int(os.environ["MYSQL_PORT"]),
                           user=os.environ["MYSQL_USER"],
                           passwd=os.environ["MYSQL_PASS"],
                           database=os.environ["MYSQL_DB"]
                           )
    cursor = conn.cursor()
    cursor.execute("""select court, check_date, section_name, order_num, case_num, hearing_time, hearing_place,
                case_info, stage, judge, hearing_result, decision_link, case_link 
                from dm_court_cases
                where lower(case_num) like lower(%(case_num)s)
                order by check_date desc
                limit %(limit)s""", {"case_num": case_num, "limit": bot_config.OUTPUT_LIMIT})

    result = cursor.fetchall()

    if not result:
        message = "Ничего не найдено."
        await update.effective_message.reply_text(message)
        return

    for row in result:
        message = form_message_from_db_response(row)
        await update.effective_message.reply_text(message)
    cursor.close()
    conn.close()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Starts the conversation."""

    await update.effective_message.reply_text(
        "Добро пожаловать в систему уведомлений судебных заседаний.\n\n"
        "Для поиска судебного дела используйте команду /search <номер дела>.\n"
        "Для подписки на уведомления по делу - /subscribe <номер дела>.\n"
        "Для прекращения подписки по делу - /unsubscribe <номер дела>.\n"
        "Для прекращения всех подписок - /unsubscribe all.\n"
        "Для просмотра списка подписок - /list.\n"
        "Для просмотра статистики базы - /status."
    )


def main() -> None:
    """Run the bot."""

    logger.info("Starting [Courts Info Service:: Telegram Bot].")

    # Load environment variables from .env_hosting file from the project root dir
    load_dotenv()

    # debug output for loaded variables
    logger.info(f"Loaded environment variables:\n"
                f"API_TOKEN={'OK' if os.environ['API_TOKEN'] else '!!!'}\n"  # will raise KeyError if no token
                f"MYSQL_HOST={os.getenv('MYSQL_HOST', 'Value Doesnt Exist!')}\n"
                f"MYSQL_PORT={os.getenv('MYSQL_PORT', 'Value Doesnt Exist!')}\n"
                f"MYSQL_USER={os.getenv('MYSQL_USER', 'Value Doesnt Exist!')}\n"
                f"MYSQL_PASS={os.getenv('MYSQL_PASS', 'Value Doesnt Exist!')}\n"
                f"MYSQL_DB={os.getenv('MYSQL_DB', 'Value Doesnt Exist!')}\n")

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.environ['API_TOKEN']).build()

    # Register the commands
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("list", show_subscriptions))
    application.add_handler(CommandHandler("subscribe", add_subscription))
    application.add_handler(CommandHandler("unsubscribe", remove_subscription))
    application.add_handler(CommandHandler("status", get_status))

    # schedule notification job
    application.job_queue.run_repeating(check_subscriptions, interval=bot_config.JOB_SCHEDULE_INTERVAL)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()

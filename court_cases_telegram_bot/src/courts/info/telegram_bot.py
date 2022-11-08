#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Courts Info Service:: Telegram Bot main module.
    Useful info:
        - (.env support) https://github.com/theskumar/python-dotenv

    Created:  Sokolov Sergei, 01.10.2022
    Modified: Dmitrii Gusev, 05.11.2022
"""

import os
import pymysql
import logging

from dotenv import load_dotenv
from prettytable import PrettyTable
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from pymysql.connections import Connection
from pymysql.cursors import Cursor
from courts.info.config import bot_config
from courts.info import VERSION

# Enable logging
# todo: implement logger config
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# useful constants
# ENV_SETTINGS_FILE = ".env.local"
ENV_SETTINGS_FILE = ".env.prod"


def form_message_from_db_response(row) -> str:
    """dm.court, dm.check_date, dm.section_name, dm.order_num, dm.case_num,
       dm.hearing_time, dm.hearing_place, dm.case_info, dm.stage, dm.judge, dm.hearing_result,
       dm.decision_link, dm.case_link, dm.row_hash, dm.court_alias"""
    message = "Суд: " + str(row[0]) + "\nДата заседания: " + row[1].isoformat() + "\nНомер дела: " + str(row[4])
    if row[2] and len(row[2]) > 0:
        message = message + "\nКатегория: " + str(row[2])
    if row[3]:
        message = message + "\nПорядковый номер: " + str(row[3])
    if row[5] and len(row[5]) > 0:
        message = message + "\nВремя слушания: " + str(row[5])
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
    if row[12] and len(row[12]) > 0:
        message = message + "\nСсылка на дело: " + str(row[12])
    return message


def get_mysql_conn():
    """Utility method: returning new mysql connection."""

    return pymysql.connect(host=os.environ["MYSQL_HOST"], port=int(os.environ["MYSQL_PORT"]),
                           user=os.environ["MYSQL_USER"], passwd=os.environ["MYSQL_PASS"],
                           database=os.environ["MYSQL_DB"])


async def version(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return Telegram Bot version string."""

    await update.effective_message.reply_text(f'Bot version: {VERSION}')


async def check_subscriptions(context: ContextTypes.DEFAULT_TYPE) -> None:
    """sends notifications for subscriptions"""

    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute("""select account_id, case_num, court, add_dttm
                    from config_telegram_bot_subscriptions""")

    subscriptions = cursor.fetchall()

    if not subscriptions:
        return

    for subscription in subscriptions:
        cursor.execute("""
                    select  dm.court, dm.check_date, dm.section_name, dm.order_num, dm.case_num, 
                            dm.hearing_time, dm.hearing_place, dm.case_info, dm.stage, dm.judge, 
                            dm.hearing_result, dm.decision_link, dm.case_link, dm.row_hash, dm.court_alias
                    from dm_court_cases dm
                        left join config_telegram_bot_notification_log nlog
                            on dm.case_num = nlog.case_num
                                and dm.court_alias = nlog.court_alias
                                and dm.check_date = nlog.check_date
                                and coalesce(dm.order_num, 0) = coalesce(nlog.order_num, 0)
                    where lower(dm.case_num) = %(case_num)s
                        and (%(court)s = 'any'
                            or dm.court_alias like '%%'|| %(court)s ||'%%'
                            or lower(dm.court) like '%%'|| %(court)s ||'%%'
                        )
                        and (nlog.row_hash is null or nlog.row_hash <> dm.row_hash)
                        and dm.load_dttm > %(sub_dttm)s
                    order by dm.check_date desc
                    limit %(limit)s
                    """,
                       {"case_num": subscription[1], "limit": bot_config.OUTPUT_LIMIT,
                        "court": subscription[2], "sub_dttm": subscription[3]})
        result_1 = cursor.fetchall()
        if result_1:
            for row in result_1:
                message = form_message_from_db_response(row)
                await context.bot.send_message(subscription[0], text=message)
                cursor.execute("""insert into config_telegram_bot_notification_log 
                                (account_id, case_num, check_date, court_alias, order_num, row_hash, send_dttm)
                                values (%(account_id)s, %(case_num)s, %(check_date)s, 
                                    %(court_alias)s, %(order_num)s, %(row_hash)s, now())""",
                               {"account_id": str(subscription[0]), "case_num": str(subscription[1]),
                                "check_date": row[1], "court_alias": row[14],
                                "order_num": row[3], "row_hash": row[13]})
                conn.commit()
    cursor.close()
    conn.close()


async def add_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """adds new subscription"""
    account_id = str(update.message.from_user.id)
    input_args = " ".join(context.args)
    case_num = input_args.split("==")[0].strip().lower()
    if len(input_args.split("==")) > 1:
        court = input_args.split("==")[1].strip().lower()
    else:
        court = "any"

    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute("""insert into config_telegram_bot_subscriptions (account_id, case_num, court)
            select %(account_id)s, %(case_num)s, %(court)s
            from dual
            where not exists (select 1 from config_telegram_bot_subscriptions 
                where account_id = %(account_id)s 
                and lower(case_num) = %(case_num)s
                and lower(court) = %(court)s
                limit 1)""",
                   {"case_num": case_num, "account_id": account_id, "court": court})
    conn.commit()
    if court == "any":
        await update.effective_message.reply_text(f"Добавлена подписка на дело {case_num}")
    else:
        await update.effective_message.reply_text(f"Добавлена подписка на дело {case_num} в суде {court}")
    cursor.close()
    conn.close()


async def remove_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """removes subscription"""
    account_id = str(update.message.from_user.id)
    input_args = " ".join(context.args)
    case_num = input_args.split("==")[0].strip().lower()
    if len(input_args.split("==")) > 1:
        court = input_args.split("==")[1].strip().lower()
    else:
        court = "any"

    conn = get_mysql_conn()
    cursor = conn.cursor()
    if case_num == "all":
        cursor.execute("""delete from config_telegram_bot_subscriptions 
                            where account_id = %(account_id)s""",
                       {"account_id": account_id})
        conn.commit()
        await update.effective_message.reply_text(f"Все подписки удалены. Вы больше не будете получать уведомлений.")
    else:
        cursor.execute("""delete from config_telegram_bot_subscriptions 
                    where account_id = %(account_id)s 
                    and lower(case_num) = lower(%(case_num)s)
                    and (%(court)s = 'any'
                        or court = %(court)s
                        )
                    """,
                       {"case_num": case_num, "account_id": account_id, "court": court})
        conn.commit()
        await update.effective_message.reply_text(f"Удалена подписка на дело {case_num}")
    cursor.close()
    conn.close()


async def get_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """shows active subs"""

    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute("""select count(*) as total_rows,
                    date_format(max(load_dttm),'%d.%m.%Y %H:%i') as last_load_dttm,
                    date_format(min(check_date),'%d.%m.%Y') as min_dt,
                    date_format(max(check_date),'%d.%m.%Y') as max_dt
                    from dm_court_cases""")

    result = cursor.fetchall()
    row = result[0]
    message = f"Последнее обновление: {row[1]}\n" \
              f"Слушания от {row[2]} до {row[3]}\n" \
              f"Всего записей: {str(row[0])}\n" \
              f"User: {update.message.from_user.name} ({update.message.from_user.full_name})"

    await update.effective_message.reply_text(message)
    cursor.close()
    conn.close()


async def get_full_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """shows active subs"""

    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute("select title, total_rows, min_dt, max_dt from dm_v_court_stats")

    result = cursor.fetchall()

    table = PrettyTable(["Суд", "Всего записей", "Слушания с", "Слушания по"])
    table.align["Суд"] = 'l'
    table.align["Всего записей"] = 'r'
    table.align["Слушания с"] = 'r'
    table.align["Слушания по"] = 'r'

    for row in result:
        table.add_row([row[0], row[1], row[2], row[3]])
        if len(str(table)) > 5000:
            message = f"```{table}```"
            await update.effective_message.reply_text(message, parse_mode="markdown")
            table.clear_rows()

    message = f"```{str(table)}```"
    await update.effective_message.reply_text(message, parse_mode="markdown")
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
    cursor.execute("""select case_num, court from config_telegram_bot_subscriptions 
                where account_id = %(account_id)s""",
                   {"account_id": account_id})

    result = cursor.fetchall()

    if not result:
        message = "Подписок нет."
        await update.effective_message.reply_text(message)
        return
    message = "Вы подписаны на:"
    for row in result:
        if row[1] == "any":
            message = message + "\nДело номер " + row[0]
        else:
            message = message + "\nДело номер " + row[0] + ", суд: " + row[1]
    await update.effective_message.reply_text(message)
    cursor.close()
    conn.close()


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """searches for court case"""

    # args should contain the case number
    case_num = " ".join(context.args)

    conn = get_mysql_conn()
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
    load_dotenv(dotenv_path=ENV_SETTINGS_FILE, verbose=True)

    # debug output for loaded variables
    logger.info(f"Loaded environment variables:\n"
                # will raise KeyError if no token
                f"API_TOKEN={'OK' if os.environ['API_TOKEN'] else 'No API Token provided!'}\n"
                f"MYSQL_HOST={os.getenv('MYSQL_HOST', 'Value Doesnt Exist!')}\n"
                f"MYSQL_PORT={os.getenv('MYSQL_PORT', 'Value Doesnt Exist!')}\n"
                f"MYSQL_DB={os.getenv('MYSQL_DB', 'Value Doesnt Exist!')}\n"
                f"MYSQL_USER={os.getenv('MYSQL_USER', 'Value Doesnt Exist!')}\n"
                # will raise KeyError if no password
                f"MYSQL_PASS={'OK' if os.environ['MYSQL_PASS'] else 'No MySql Password provided!'}\n")

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.environ['API_TOKEN']).build()

    # Register the commands
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("list", show_subscriptions))
    application.add_handler(CommandHandler("subscribe", add_subscription))
    application.add_handler(CommandHandler("unsubscribe", remove_subscription))
    application.add_handler(CommandHandler("status", get_status))
    application.add_handler(CommandHandler("version", version))

    # schedule notification job
    application.job_queue.run_repeating(check_subscriptions, interval=bot_config.JOB_SCHEDULE_INTERVAL)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()

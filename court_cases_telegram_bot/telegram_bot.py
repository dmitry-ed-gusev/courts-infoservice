from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import pymysql
import logging

from court_cases_telegram_bot import config

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

conn = pymysql.connect(host=config.MYSQL_CONNECT["host"],
                       port=config.MYSQL_CONNECT["port"],
                       user=config.MYSQL_CONNECT["user"],
                       passwd=config.MYSQL_CONNECT["passwd"]
                       )

cursor = conn.cursor()


async def check_subscriptions(context: ContextTypes.DEFAULT_TYPE) -> None:
    """sends notifications for subscriptions"""
    cursor.execute("""select account_id, case_num, last_notification_dttm 
                    from dm.telegram_bot_subscriptions""")

    result = cursor.fetchall()

    if not result:
        return

    for row in result:
        cursor.execute("""select court, check_date, section_name, order_num, case_num, hearing_time, hearing_place,
                        case_info,judge, hearing_result, decision_link, case_link 
                        from dm.court_cases
                        where lower(case_num) like lower(%(case_num)s)
                        and load_dttm > %(last_check_dttm)s
                        order by check_date desc
                        limit %(limit)s""",
                       {"case_num": str(row[1]), "limit": config.OUTPUT_LIMIT,
                        "last_check_dttm": row[2]})
        result_1 = cursor.fetchall()
        if result_1:
            for row1 in result_1:
                message = "Суд: " + str(row[0]) + "\nДата заседания: " + row1[1].isoformat() + "\nКатегория: " + str(
                    row1[2]) + "\nПорядковый номер: " + str(
                    row1[3]) + "\nНомер дела: " + str(row1[4]) + "\nВремя слушания: " + str(
                    row1[5]) + "\nМесто проведения: " + str(
                    row1[6]) + "\nИнформация по делу: " + str(row1[7]) + "\nСудья: " + str(
                    row1[8]) + "\nРезультат слушания: " + str(
                    row1[9]) + "\nСудебный акт: " + str(row1[10]) + "\nСсылка на дело: " + str(row1[11])
                await context.bot.send_message(row[0], text=message)
            cursor.execute("""update dm.telegram_bot_subscriptions 
                            set last_notification_dttm = now()
                            where account_id = %(account_id)s and case_num = %(case_num)s""",
                           {"case_num": str(row[1]), "account_id": str(row[0])})
            conn.commit()


async def add_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """adds new subscription"""
    account_id = str(update.message.from_user.id)
    case_num = " ".join(context.args)
    cursor.execute("""insert into dm.telegram_bot_subscriptions (account_id, case_num, last_notification_dttm)
            select %(account_id)s, lower(%(case_num)s), now() from dual
            where not exists (select * from dm.telegram_bot_subscriptions 
            where account_id = %(account_id)s and lower(case_num) = lower(%(case_num)s) limit 1)""",
                   {"case_num": case_num, "account_id": account_id})
    conn.commit()
    await update.effective_message.reply_text(f"Добавлена подписка на дело {case_num}")


async def remove_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """removes subscription"""
    account_id = str(update.message.from_user.id)
    case_num = " ".join(context.args)

    if case_num == "all":
        cursor.execute("""delete from dm.telegram_bot_subscriptions 
                            where account_id = %(account_id)s""",
                       {"account_id": account_id})
        conn.commit()
        await update.effective_message.reply_text(f"Все подписки удалены. Вы больше не будете получать уведомлений.")
    else:
        cursor.execute("""delete from dm.telegram_bot_subscriptions 
                    where account_id = %(account_id)s and lower(case_num) = lower(%(case_num)s)""",
                       {"case_num": case_num, "account_id": account_id})
        conn.commit()
        await update.effective_message.reply_text(f"Удалена подписка на дело {case_num}")


async def show_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """shows active subs"""
    account_id = str(update.message.from_user.id)
    cursor.execute("""select case_num from dm.telegram_bot_subscriptions 
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


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """searches for court case"""

    # args should contain the case number
    case_num = " ".join(context.args)

    cursor.execute("""select court, check_date, section_name, order_num, case_num, hearing_time, hearing_place,
                case_info,judge, hearing_result, decision_link, case_link 
                from dm.court_cases
                where lower(case_num) like lower(%(case_num)s)
                order by check_date desc
                limit %(limit)s""", {"case_num": case_num, "limit": config.OUTPUT_LIMIT})

    result = cursor.fetchall()

    if not result:
        message = "Ничего не найдено."
        await update.effective_message.reply_text(message)
        return

    for row in result:
        message = "Суд: " + str(row[0]) + "\nДата заседания: " + row[1].isoformat() + "\nКатегория: " + str(
            row[2]) + "\nПорядковый номер: " + str(
            row[3]) + "\nНомер дела: " + str(row[4]) + "\nВремя слушания: " + str(
            row[5]) + "\nМесто проведения: " + str(
            row[6]) + "\nИнформация по делу: " + str(row[7]) + "\nСудья: " + str(
            row[8]) + "\nРезультат слушания: " + str(
            row[9]) + "\nСудебный акт: " + str(row[10]) + "\nСсылка на дело: " + str(row[11])
        await update.effective_message.reply_text(message)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Starts the conversation."""

    await update.effective_message.reply_html(
        "Welcome to court cases bot. \n\n"
        "Use /search case_num to look for case.\n"
        "Use /subscribe case_num to subscribe for case updates.\n"
        "Use /unsubscribe case_num to unsubscribe for case updates.\n"
        "Use /unsubscribe all to unsubscribe for all cases updates.\n"
        "use /list to see current subscriptions."
    )


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(config.API_TOKEN).build()

    # Register the commands
    application.add_handler(CommandHandler(["start", "help"], start))

    application.add_handler(CommandHandler("search", search))

    application.add_handler(CommandHandler("list", show_subscriptions))

    application.add_handler(CommandHandler("subscribe", add_subscription))

    application.add_handler(CommandHandler("unsubscribe", remove_subscription))

    # schedule notification job
    application.job_queue.run_repeating(check_subscriptions, interval=config.JOB_SCHEDULE_INTERVAL)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()

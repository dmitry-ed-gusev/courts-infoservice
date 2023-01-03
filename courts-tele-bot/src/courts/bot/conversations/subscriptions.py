from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from courts.bot.config import bot_config
from courts.bot.utils.utilities import get_mysql_conn, form_message_from_db_response


async def add_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """adds new subscription"""
    input_text = update.message.text
    account_id = str(update.message.from_user.id)

    conn = get_mysql_conn()
    cursor = conn.cursor()

    for input_row in input_text.split("\n"):
        case_num = input_row.split("==")[0].strip().lower()
        if len(input_row.split("==")) > 1:
            court = input_row.split("==")[1].strip().lower()
        else:
            court = "any"

        cursor.execute(
            """insert into config_telegram_bot_subscriptions (account_id, case_num, court, add_dttm)
                select %(account_id)s, %(case_num)s, %(court)s, now()
                from dual
                where not exists (select 1 from config_telegram_bot_subscriptions 
                    where account_id = %(account_id)s 
                    and lower(case_num) = %(case_num)s
                    and lower(court) = %(court)s
                    limit 1)""",
            {"case_num": case_num, "account_id": account_id, "court": court},
        )
        conn.commit()
        if court == "any":
            await update.message.reply_text(f"Добавлена подписка на дело {case_num}")
        else:
            await update.message.reply_text(
                f"Добавлена подписка на дело {case_num} в суде {court}"
            )
    cursor.close()
    conn.close()


async def remove_subscription(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """removes subscription"""
    query = update.callback_query
    await query.answer()

    input_text = query.message.text
    account_id = str(query.message.from_user.id)
    conn = get_mysql_conn()
    cursor = conn.cursor()
    for input_row in input_text.split("\n"):
        case_num = input_row.split("==")[0].strip().lower()
        if len(input_row.split("==")) > 1:
            court = input_row.split("==")[1].strip().lower()
        else:
            court = "any"

        if case_num == "all":
            cursor.execute(
                """delete from config_telegram_bot_subscriptions 
                   where account_id = %(account_id)s""",
                {"account_id": account_id},
            )
            conn.commit()
            await query.message.reply_text(
                f"Все подписки удалены. Вы больше не будете получать уведомлений."
            )
        else:
            cursor.execute(
                """delete from config_telegram_bot_subscriptions 
                    where account_id = %(account_id)s 
                    and lower(case_num) = lower(%(case_num)s)
                    and (%(court)s = 'any'
                        or court = %(court)s
                        )
                """,
                {"case_num": case_num, "account_id": account_id, "court": court},
            )
            conn.commit()
            await query.message.reply_text(f"Удалена подписка на дело {case_num}")
    cursor.close()
    conn.close()


async def remove_subscription_all(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """removes all subscriptions"""
    query = update.callback_query
    await query.answer()
    account_id = str(query.from_user.id)

    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute(
        """delete from config_telegram_bot_subscriptions 
                            where account_id = %(account_id)s""",
        {"account_id": account_id},
    )
    conn.commit()
    cursor.close()
    conn.close()
    await query.message.reply_text(
        f"Все подписки удалены. Вы больше не будете получать уведомлений."
    )


async def show_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """shows active subs"""
    query = update.callback_query
    await query.answer()
    account_id = str(query.from_user.id)
    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute(
        """select case_num, court 
               from config_telegram_bot_subscriptions 
               where account_id = %(account_id)s
            """,
        {"account_id": account_id},
    )

    result = cursor.fetchall()
    cursor.close()
    conn.close()
    if not result:
        message = "Подписок нет."
        await query.message.reply_text(message)
        return "SUBS"
    message = "Вы подписаны на:"
    for row in result:
        if row[1] == "any":
            message = message + "\nДело номер " + row[0]
        else:
            message = message + "\nДело номер " + row[0] + ", суд: " + row[1]
    await query.message.reply_text(message)
    return "SUBS"


async def conv_subs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Subscribe conversation."""
    query = update.callback_query
    await query.answer()
    message = "Меню управления подписсками."

    keyboard = [
        [
            InlineKeyboardButton(text="\U0001F4E8 Просмотр подписок", callback_data="SUB_LIST"),
            InlineKeyboardButton(text="\U0001F4EC Добавить подписку", callback_data="SUB_ADD"),
        ],
        [
            InlineKeyboardButton(text="\U0001F4ED Удалить подписку", callback_data="SUB_REMOVE"),
            InlineKeyboardButton(text="\U0001F5D9 Удалить все подписки", callback_data="SUB_REMOVE_ALL"),
        ],
        [
            InlineKeyboardButton(text="\U000021A9 Назад", callback_data="START"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=message, reply_markup=reply_markup)
    return "SUBS"


async def conv_add_subscription(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    """Add subscription conversation."""
    query = update.callback_query
    await query.answer()
    message = (
        "Введите номер дела (и, при желании, часть имени суда)."
        "\nПримеры:\nА63-10004/2021\n1-1207/2022 == Санкт-Петербург"
    )

    keyboard = [
        [
            InlineKeyboardButton(text="\U000021A9 Назад", callback_data="SUBS"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=message, reply_markup=reply_markup)
    return "SUBS_ADD"


async def conv_remove_subscription(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    """Add subscription conversation."""
    query = update.callback_query
    await query.answer()
    message = (
        "Введите номер дела и имя суда."
        "\nПримеры:\nА63-10004/2021\n1-1207/2022 == Санкт-Петербург"
    )

    keyboard = [
        [
            InlineKeyboardButton(text="\U000021A9 Назад", callback_data="SUBS"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=message, reply_markup=reply_markup)
    return "SUBS_REMOVE"


async def check_subscriptions(context: ContextTypes.DEFAULT_TYPE) -> None:
    """sends notifications for subscriptions"""

    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute(
        "select account_id, case_num, court, add_dttm "
        "from config_telegram_bot_subscriptions"
    )
    subs = cursor.fetchall()

    if not subs:
        return

    for subscription in subs:
        cursor.execute(
            """
                select  dm.court, dm.check_date, dm.section_name, dm.order_num, dm.case_num, 
                        dm.hearing_time, dm.hearing_place, dm.case_info, dm.stage, dm.judge, 
                        dm.hearing_result, dm.decision_link, dm.case_link, dm.row_hash, dm.court_alias
                from dm_v_court_cases dm
                where lower(dm.case_num) = %(case_num)s
                    and (%(court)s = 'any'
                        or dm.court_alias like %(court_like)s
                        or lower(dm.court) like %(court_like)s
                    )
                    and dm.load_dttm > %(sub_dttm)s
                    and not exists (
                        select nlog.case_num
                        from config_telegram_bot_notification_log nlog
                        where dm.case_num = nlog.case_num
                            and dm.court_alias = nlog.court_alias
                            and dm.check_date = nlog.check_date
                            and coalesce(dm.order_num, 0) = coalesce(nlog.order_num, 0)
                            and nlog.row_hash = dm.row_hash
                            and nlog.inactive_flag = false
                    )
                order by dm.check_date asc
                limit %(limit)s
            """,
            {
                "case_num": subscription[1],
                "limit": bot_config.OUTPUT_LIMIT,
                "court": subscription[2],
                "court_like": f"%{subscription[2]}%",
                "sub_dttm": subscription[3],
            },
        )
        result_1 = cursor.fetchall()
        if result_1:
            for row in result_1:
                message = form_message_from_db_response(row)
                await context.bot.send_message(subscription[0], text=message)
                cursor.execute(
                    """insert into config_telegram_bot_notification_log 
                            (account_id, case_num, check_date, court_alias, order_num, row_hash, send_dttm)
                            values (%(account_id)s, %(case_num)s, %(check_date)s, 
                                %(court_alias)s, %(order_num)s, %(row_hash)s, now())""",
                    {
                        "account_id": str(subscription[0]),
                        "case_num": str(subscription[1]),
                        "check_date": row[1],
                        "court_alias": row[14],
                        "order_num": row[3],
                        "row_hash": row[13],
                    },
                )
                conn.commit()
    cursor.close()
    conn.close()

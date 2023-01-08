import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from courts.bot.config import bot_config
from courts.bot.utils.utilities import get_mysql_conn, form_message_from_db_response


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """searches for court case"""
    case_num = f"%{update.message.text.lower()}%"
    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute(
        """select dm.court, dm.check_date, dm.section_name, dm.order_num, dm.case_num,
                dm.hearing_time, dm.hearing_place, dm.case_info, dm.stage, dm.judge, dm.hearing_result,
                dm.decision_link, dm.case_link, dm.row_hash, dm.court_alias
           from dm_v_court_cases dm
           where lower(dm.case_num) like %(case_num)s
           order by dm.check_date desc
           limit %(limit)s
        """,
        {"case_num": case_num, "limit": bot_config.OUTPUT_LIMIT},
    )

    result = cursor.fetchall()
    cursor.close()
    conn.close()

    if not result:
        message = "Ничего не найдено."
        await update.message.reply_text(message)
        return "SEARCH"

    for row in result:
        message = form_message_from_db_response(row)
        await update.message.reply_text(message)

    return "SEARCH"


async def conv_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Search conversation."""
    query = update.callback_query
    await query.answer()
    message = "Введите номер дела для поиска"

    keyboard = [
        [
            InlineKeyboardButton(text="\U000021A9 Назад", callback_data="START"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=message, reply_markup=reply_markup)
    return "SEARCH"

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from courts.bot.utils.utilities import get_mysql_conn


async def link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """create link with site account"""

    username = update.message.text.lower()
    account_id = str(update.message.from_user.id)

    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute(
        """delete from config_telegram_bot_account_link  
            where account_id = %(account_id)s 
        """,
        {"account_id": account_id},
    )
    conn.commit()
    cursor.execute(
        """insert into config_telegram_bot_account_link (username, account_id)
            select lower(%(username)s), %(account_id)s
            from dual
            where not exists (select 1 from config_telegram_bot_account_link 
                where account_id = %(account_id)s 
                and lower(username) = lower(%(username)s)
                limit 1)""",
        {"account_id": account_id, "username": username},
    )
    conn.commit()
    cursor.close()
    conn.close()
    await update.message.reply_text(f"Связь с аккаунтом {username} установлена.")


async def unlink(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """delete link with site account"""
    query = update.callback_query
    await query.answer()
    account_id = str(query.from_user.id)

    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute(
        """delete from config_telegram_bot_account_link  
            where account_id = %(account_id)s 
        """,
        {"account_id": account_id},
    )
    conn.commit()
    cursor.close()
    conn.close()
    await query.message.reply_text(f"Связь с аккаунтом удалена.")
    return "LINKS"


async def conv_links(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Link conversation."""
    query = update.callback_query
    await query.answer()
    account_id = str(query.from_user.id)
    conn = get_mysql_conn()
    cursor = conn.cursor()
    cursor.execute(
        """select username 
           from config_telegram_bot_account_link  
           where account_id = %(account_id)s 
        """,
        {"account_id": account_id},
    )
    result = cursor.fetchall()

    message = "Для привязки аккаунта введите имя пользователя."
    if len(result) > 0:
        row = result[0]
        message += f"\nЭтот чат связан с аккаунтом {row[0]}"
    else:
        message += f"\nЧат не связан с аккаунтом сайта."

    keyboard = [
        [
            InlineKeyboardButton(text="\U0001F5D9 Отвязать аккаунт", callback_data="REMOVE_LINK"),
        ],
        [
            InlineKeyboardButton(text="\U000021A9 Назад", callback_data="START"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text=message, reply_markup=reply_markup)
    return "LINKS"

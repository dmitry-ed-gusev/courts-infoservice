from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Starts the conversation."""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
    else:
        query = update
    message = "Добро пожаловать в систему уведомлений судебных заседаний."

    keyboard = [
        [
            InlineKeyboardButton(text="\U0001f50d Поиск решений", callback_data="SEARCH"),
            InlineKeyboardButton(text="\U00002709 Подписки", callback_data="SUBS"),
        ],
        [
            InlineKeyboardButton(text="\U0001F517 Привязка аккаунта", callback_data="LINKS"),
            InlineKeyboardButton(text="\U0001F5E0 Статистика", callback_data="STATS"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(text=message, reply_markup=reply_markup)
    return "START"


async def conv_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Starts the conversation editing prev message."""
    query = update.callback_query
    await query.answer()

    message = "Добро пожаловать в систему уведомлений судебных заседаний."

    keyboard = [
        [
            InlineKeyboardButton(text="\U0001f50d Поиск решений", callback_data="SEARCH"),
            InlineKeyboardButton(text="\U00002709 Подписки", callback_data="SUBS"),
        ],
        [
            InlineKeyboardButton(text="\U0001F517 Привязка аккаунта", callback_data="LINKS"),
            InlineKeyboardButton(text="\U0001F5E0 Статистика", callback_data="STATS"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=message, reply_markup=reply_markup)
    return "START"

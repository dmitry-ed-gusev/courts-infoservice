from telegram import Update
from telegram.ext import ContextTypes

from courts.bot import VERSION


async def version(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Return Telegram Bot version string."""

    await update.effective_message.reply_text(f"Bot version: {VERSION}")

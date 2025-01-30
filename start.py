from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import datetime

from states import MAINMENU
from bd import create_user
from logging_file import logger


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    TimeOfDay = datetime.datetime.now().hour
    if TimeOfDay < 12:
        TimeOfDay = "Доброе утро ☀️"
    elif TimeOfDay < 17:
        TimeOfDay = "Добрый день🌍"
    elif TimeOfDay < 22:
        TimeOfDay = "Добрый вечер🌒"
    elif TimeOfDay < 5:
        TimeOfDay = "Доброй ночи🌚"

    keyboard = [
        [InlineKeyboardButton("установить таймер", callback_data="set_timer")],
        [InlineKeyboardButton("мои таймеры", callback_data="check")],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    if not query or query.data == "no":
        await create_user(update.effective_user.id, update.effective_user.name)
        logger.info(f"Пользователь {update.effective_user.id} запустил бота")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{TimeOfDay}, {update.effective_user.username}! В этом боте ты сможешь выбрать отсчет до/от какого-то дня и получать ежедневные сообщения ⏳",
            reply_markup=markup,
        )
    else:
        await query.edit_message_text(
            text=f"{TimeOfDay}, {update.effective_user.username}! Вы можете добавить или просмотреть ваши даты ⏳",
            reply_markup=markup,
        )

    return MAINMENU

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

import datetime 

from states import MAINMENU 
from bd import create_user, create_timer
from logging_file import logger


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    create_user(update.effective_user.id, update.effective_user.name)
    logger.info(f'Пользователь {update.effective_user.id} запустил бота')
    TimeOfDay = datetime.datetime.now().hour
    if TimeOfDay <= 5: 
        TimeOfDay = "Доброе утро"
    elif TimeOfDay <= 12:
        TimeOfDay = 'Добрый день'
    elif TimeOfDay <= 17:
        TimeOfDay = 'Добрый вечер'
    elif TimeOfDay <= 22:
        TimeOfDay = 'Доброй ночи'
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"{TimeOfDay}, {update.effective_user.username}! В этом боте ты сможешь выбрать отсчет до/от какого-то дня и получать ежедневное сообщение.\n\n/set_time - установать время\n/check - посмотреть свои даты"
    )

    return MAINMENU
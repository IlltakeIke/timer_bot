import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
)
from telegram.ext import (
    ContextTypes,
)
import datetime

from dotenv import load_dotenv
from states import MAINMENU, SETTIME, GETTIME
from start import start

from constants import regular_data
from bd import get_all_timers
import pytz

async def send_all_notif(context: ContextTypes.DEFAULT_TYPE):
    users_data = get_all_timers()
    for user, date in users_data:
        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S') 
        date_now = datetime.datetime.now()
        delta = date_obj - date_now
        await context.bot.send_message(
            chat_id=user,
            text=f'check users with timers, your date - {date}\nДо него осталось {delta.days} дней, {delta.seconds // 3600} часов, {delta.seconds%3600} '
    )
    # Сделать запрос с БД и достать список id всех людей у кого есть сейчас действующие таймеры
    # Сделать рассылку по этим людям
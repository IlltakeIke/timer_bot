import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
from states import MAINMENU, SETTIME, GETDATE, GETTIME, GETMESS, CHOICE, CHECK
from start import start
from set_time import set_time, get_date, get_time, skip_time, get_mess, skip_mess, choice, get_time_notif
from constants import regular_data
from bd import create_table, check_timers
import pytz
from all_jobs import send_all_notif
from logging_file import logger
from babel.dates import format_datetime

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = []
    user_timers = await check_timers(update.effective_user.id)
    text = ''
    i = 1
    for timer in user_timers:
        date_obj = datetime.datetime.strptime(timer[2],'%Y-%m-%d %H:%M:%S') 
        mess = timer[0] if timer[0] != 'Ваш таймер истек' else f'Таймер {timer[1]} - {format_datetime(date_obj, 'hh:mm:ss d MMMM y года', locale='ru')}'
        if mess == '[]':
            mess = timer[2]
        text += f'{i}. {mess}\n'
        button = InlineKeyboardButton(f'Таймер {timer[1]}', callback_data=f'{timer[1]}')
        keyboard.append([button])
        i += 1
    if not text: 
        text = 'У вас пока нет дат'

    keyboard.append([InlineKeyboardButton('Назад', callback_data='back')])
    markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=f"{text}",
        reply_markup=markup
    )
    return CHECK
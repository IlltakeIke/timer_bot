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
import pytz

from bd import create_user, create_timer, get_one_timers, remove_timer
from states import MAINMENU, SETTIME, GETDATE, GETTIME, GETMESS, CHOICE
from all_jobs import send_all_notif
from start import start
from all_jobs import timer_call, counter
from check import check

async def confirm_delete_timer(update, context):
    query = update.callback_query
    id_timer = int(query.data)
    context.user_data['id_timer'] = id_timer
    keyboard = [[InlineKeyboardButton('удалить 🗑', callback_data='remove')], [InlineKeyboardButton('отмена ❌', callback_data='cancel')]]
    markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text="Точно ли хотите удалить таймер?",
        reply_markup=markup
    )

async def delete_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    id_timer = context.user_data['id_timer']
    query = update.callback_query
    await query.answer()
    jobs = context.job_queue.get_jobs_by_name(f'job_{id_timer}') 
    for job in jobs:
        job.schedule_removal()
    jobs = context.job_queue.get_jobs_by_name(f'job_ro_{id_timer}') 
    for job in jobs:
        job.schedule_removal()
    await remove_timer(id_timer)
    await check(update, context)
    
    
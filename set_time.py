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

from states import MAINMENU, SETTIME, GETTIME
from all_jobs import send_all_notif

async def set_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Введи дату из будущего или прошлого (В формате: \n DD.MM.YYYY \n DDMMYYYY)"
    )
    return GETTIME
    

async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pers_date = ''
    answer = update.effective_message.text
    answer = answer.lower()
    if '.' in answer:
        answer = answer.split('.')
    else:
        answer = answer[:2], answer[2:4], answer[4:8]

    for i in range(3):
        pers_date += answer[i] + '.'
    pers_date = pers_date[:-1]
    context.user_data['pers_data'] = pers_date
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text = f'вот - {pers_date}'
    )

async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass

async def put_timer_to_bd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass
    

    



    
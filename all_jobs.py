from logging_file import logger
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
from bd import get_all_timers, active
import pytz

async def send_all_notif(context: ContextTypes.DEFAULT_TYPE):#сделать на подобие новую функ-ю для одного человека без запроса в бд и бещ цикла 
    users_data = get_all_timers()
    for user, date in users_data:
        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S') 
        date_now = datetime.datetime.now()
        delta = date_obj - date_now
        await context.bot.send_message(
            chat_id=user,
            text=f'check users with timers, your date - {date}\nДо него осталось {delta.days} дней, {delta.seconds // 3600} часов, {delta.seconds%3600} '
    )
        
async def timer_call(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(
        chat_id=job.chat_id,
        text=job.data['message']  
    )

    id_timer = job.data['id_timer']
    jobs = context.job_queue.get_jobs_by_name('job_{id_timer}')
    for job in jobs:
        job.schedule_removal()

    point = job.data['full_date']
    if active(id_timer):
        logger.info(f'Таймер {job.data['message']} пользователя {job.chat_id} сработал')


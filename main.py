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
from states import MAINMENU, SETTIME, GETDATE, GETTIME, GETMESS, CHOICE
from start import start
from set_time import set_time, get_date, get_time, skip_time, get_mess, skip_mess, choice, get_time_notif
from constants import regular_data
from bd import create_table
import pytz
from all_jobs import send_all_notif
from logging_file import logger
from check import check

load_dotenv()



if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('TOKEN')).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAINMENU: [
                CommandHandler('set_time', set_time),
                CommandHandler('check', check)
            ],
            GETDATE: [MessageHandler(filters.Regex(regular_data), get_date)],
            GETTIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time), CommandHandler('skip', skip_time)],
            GETMESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_mess), CommandHandler('skip', skip_mess)],
            CHOICE: [CallbackQueryHandler(choice),MessageHandler(filters.TEXT & ~filters.COMMAND, get_time_notif)]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    create_table()
    # ПРОВЕРКИ КАЖДЫЕ 12.00 
    # application.job_queue.run_daily(send_all_notif, time=datetime.time(hour=12, tzinfo=pytz.timezone('Etc/GMT-3')))
    # application.job_queue.run_once(send_all_notif, datetime.timedelta(seconds=5))


    application.run_polling()
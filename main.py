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
from set_time import set_time, get_time
from constants import regular_data
from bd import create_table
import pytz
from all_jobs import send_all_notif

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)



if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv('TOKEN')).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAINMENU: [
                CommandHandler('set_time', set_time)
            ],
            GETTIME: [MessageHandler(filters.Regex(regular_data), get_time)]
            
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    create_table()
    # application.job_queue.run_daily(send_all_notif, time=datetime.time(hour=12, tzinfo=pytz.timezone('Etc/GMT-3')))
    application.job_queue.run_once(send_all_notif, datetime.timedelta(seconds=5))


    application.run_polling()
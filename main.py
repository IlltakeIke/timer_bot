import os

from dotenv import load_dotenv
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from bd import create_table
from check import check
from constants import regular_data
from set_time import (
    choice,
    get_date,
    get_mess,
    get_time,
    get_time_notif,
    set_time,
    skip_mess,
    skip_time,
)
from start import start, run_all_jobs
from states import CHOICE, GETDATE, GETMESS, GETTIME, MAINMENU, CHECK
from delete_timer import delete_timer, confirm_delete_timer
import asyncio
import datetime

load_dotenv()

def main():
    application = ApplicationBuilder().token(os.getenv('TOKEN')).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAINMENU: [
                CallbackQueryHandler(set_time, pattern='^set_timer$'),
                CallbackQueryHandler(check, pattern='^check$'),
                CallbackQueryHandler(start, pattern='^back$')
            ],
            CHECK: [CallbackQueryHandler(start, pattern='^back$'), CallbackQueryHandler(delete_timer, pattern='remove'), CallbackQueryHandler(check, pattern='cancel'), CallbackQueryHandler(confirm_delete_timer)],
            GETDATE: [MessageHandler(filters.Regex(regular_data), get_date), CallbackQueryHandler(GETTIME, pattern='^skip$')],
            GETTIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time), CallbackQueryHandler(skip_time, pattern='^skip')],
            GETMESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_mess), CallbackQueryHandler(skip_mess, pattern='^skip_time$')],
            CHOICE: [CallbackQueryHandler(choice),MessageHandler(filters.TEXT & ~filters.COMMAND, get_time_notif)]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    # ПРОВЕРКИ КАЖДЫЕ 12.00 
    # application.job_queue.run_daily(send_all_notif, time=datetime.time(hour=12, tzinfo=pytz.timezone('Etc/GMT-3')))
    # application.job_queue.run_once(send_all_notif, datetime.timedelta(seconds=5))
    application.job_queue.run_once(run_all_jobs, datetime.timedelta(seconds=1))

    application.run_polling()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_table())
    main()
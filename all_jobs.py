import datetime

from telegram.ext import (
    CallbackContext,
    ContextTypes,
)

from bd import active, get_all_timers, get_one_timers, remove_timer
from logging_file import logger


async def send_all_notif(context: ContextTypes.DEFAULT_TYPE):
    users_data = await get_all_timers()
    for user, date in users_data:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        date_now = datetime.datetime.now()
        delta = date_obj - date_now
        await context.bot.send_message(
            chat_id=user,
            text=f"check users with timers, your date - {date}\nДо него осталось {delta.days} дней, {delta.seconds // 3600} часов, {delta.seconds % 3600} ",
        )


async def send_one_notif(context: ContextTypes.DEFAULT_TYPE):
    user, date = await get_one_timers()
    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    date_now = datetime.datetime.now()
    delta = date_obj - date_now
    await context.bot.send_message(
        chat_id=user,
        text=f"check users with timers, your date - {date}\nДо него осталось {delta.days} дней, {delta.seconds // 3600} часов, {delta.seconds % 3600} ",
    )


async def timer_call(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(chat_id=job.chat_id, text=job.data["message"])

    id_timer = job.data["id_timer"]
    jobs = context.job_queue.get_jobs_by_name(f"job_{id_timer}")
    for job in jobs:
        job.schedule_removal()

    point = job.data["full_date"]
    if await active(id_timer):
        logger.info(f"Таймер {job.data['message']} пользователя {job.chat_id} сработал")

    await remove_timer(id_timer)


async def counter(context: CallbackContext):
    job = context.job
    date: datetime.datetime = job.data["full_date"]
    chat_id = job.chat_id

    if date > datetime.datetime.now():  # будущее
        difference = date - datetime.datetime.now()
        day_before = difference.days + 1
        message = job.data["message"]
        await context.bot.send_message(
            chat_id=chat_id, text=f"До {message} осталось {day_before} дней."
        )
    else:
        difference = datetime.datetime.now() - date
        day_after = difference.days
        message = job.data["message"]
        await context.bot.send_message(
            chat_id=chat_id, text=f"С {message} прошло {day_after} дней."
        )

        

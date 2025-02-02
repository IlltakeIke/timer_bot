from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import datetime
import pytz

from states import MAINMENU
from bd import create_user, get_all_timers_for_job
from logging_file import logger
from all_jobs import counter, timer_call


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    TimeOfDay = datetime.datetime.now().hour
    if TimeOfDay < 12:
        TimeOfDay = "Доброе утро ☀️"
    elif TimeOfDay < 17:
        TimeOfDay = "Добрый день🌍"
    elif TimeOfDay < 22:
        TimeOfDay = "Добрый вечер🌒"
    elif TimeOfDay < 5:
        TimeOfDay = "Доброй ночи🌚"

    keyboard = [
        [InlineKeyboardButton("установить таймер", callback_data="set_timer")],
        [InlineKeyboardButton("мои таймеры", callback_data="check")],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    if not query or query.data == "no":
        await create_user(update.effective_user.id, update.effective_user.name)
        logger.info(f"Пользователь {update.effective_user.id} запустил бота")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{TimeOfDay}, {update.effective_user.username}! В этом боте ты сможешь выбрать отсчет до/от какого-то дня и получать ежедневные сообщения ⏳",
            reply_markup=markup,
        )
    else:
        await query.edit_message_text(
            text=f"{TimeOfDay}, {update.effective_user.username}! Вы можете добавить или просмотреть ваши даты ⏳",
            reply_markup=markup,
        )

    return MAINMENU

async def run_all_jobs(context):
    all_timers = await get_all_timers_for_job()
    for timer in all_timers:
        point = datetime.datetime.strptime(timer[1], "%Y-%m-%d %H:%M:%S")

        if point > datetime.datetime.now(): 
            context.job_queue.run_once(
                timer_call,
                point,
                data={"full_date": point, "message": timer[3], "id_timer": timer[0]},
                chat_id=timer[2],
                name=f"job_ro_{timer[0]}",
            )

        time_lst = list(map(int, timer[6].split(":")))
        time = datetime.time(
            hour=time_lst[0], minute=time_lst[1], tzinfo=pytz.timezone("Etc/GMT-3")
        )

        context.job_queue.run_daily(
        counter,
        time,
        data={"full_date": point, "message": timer[3]},
        chat_id=timer[2],
        name=f"job_{timer[0]}",
    )